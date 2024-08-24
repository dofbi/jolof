import aiohttp
import asyncio
import json
from datasets import Dataset
from utils import transform_to_jsonl
import jsonlines
from argparse import ArgumentParser


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--input_file",
        type=str,
        default="word.txt",
        help="Input file containing the list of words to fetch",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="../data/dataset.jsonl",
        help="Output file to store the fetched data",
    )
    parser.add_argument(
        "--delay", type=int, default=1, help="Delay between each request in seconds"
    )
    parser.add_argument(
        "--push_to_hub", type=bool, default=True, help="Push the dataset to the hub"
    )
    parser.add_argument("--token", type=str, default="", help="Hugging Face API token")

    parser.add_argument("--repo_id", type=str, default="wolof-french-dictionary", help="The repo id name")

    return parser.parse_args()


async def fetch_word_data(session, word):
    url = f"https://corporan.huma-num.fr/findWord=DicoWolof:{word}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            print(f"Données reçues pour le mot '{word}':", data)  # Débogage
            return data
        else:
            print(
                f"Erreur lors de la récupération des données pour le mot: {word} (Code: {response.status})"
            )
            return None


async def fetch_and_write_word_data(session, word, file, delay):
    word_data = await fetch_word_data(session, word)
    if word_data:
        transformed_data = transform_to_jsonl(word_data)
        if transformed_data:
            for item in transformed_data:
                json.dump(item, file, ensure_ascii=False)
                file.write("\n")
            print(f"Données écrites pour le mot: {word}")  # Débogage
        else:
            print(f"Aucune donnée transformée pour le mot: {word}")
    else:
        print(f"Échec de la récupération des données pour le mot: {word}")

    await asyncio.sleep(delay)


async def create_jsonl_from_words(input_file, output_file, delay=1):
    with open(input_file, "r") as file:
        words = file.read().splitlines()

    async with aiohttp.ClientSession() as session:
        with open(output_file, "a", encoding="utf-8") as file:  # Ouvrir en mode append
            tasks = []
            for i, word in enumerate(words):
                print(f"Traitement du mot {i + 1}/{len(words)}: {word}")
                tasks.append(fetch_and_write_word_data(session, word, file, delay))

            await asyncio.gather(*tasks)

    print(f"Les données ont été ajoutées avec succès dans le fichier: {output_file}")


def process_jsonl_to_dataset(jsonl_file):
    french = []
    wolof = []

    with jsonlines.open(jsonl_file) as reader:
        data = list(reader)

    for line in data:
        wolof.append(str(line["input"]))
        if line["output"] is not None:
            if isinstance(line["output"], dict) and "definition" in line["output"]:
                french.append(str(line["output"]["definition"]))
            else:
                french.append(str(line["output"]))
        else:
            french.append(None)

    if len(french) != len(wolof):
        raise ValueError("The number of french and wolof sentences are not equal")

    ds = Dataset.from_dict({"wolof": wolof, "french": french})
    return ds


async def main():

    args = argument_parser()
    await create_jsonl_from_words(args.input_file, args.output_file, args.delay)
    dataset = process_jsonl_to_dataset(args.output_file)
    if args.push_to_hub:
        dataset.push_to_hub(args.repo_id, token=args.token)


if __name__ == "__main__":
    asyncio.run(main())
