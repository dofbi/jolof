import aiohttp
import asyncio
import json
from datasets import Dataset
import jsonlines


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


def transform_to_jsonl(data):
    transformed_data = []

    if isinstance(data, dict):
        lxGroups = data.get("lxGroup", [])

        # Convert lxGroups to a list if it's a single object
        if isinstance(lxGroups, dict):
            lxGroups = [lxGroups]

        for lxGroup in lxGroups:
            if isinstance(lxGroup, dict):
                psGroup = lxGroup.get("psGroup", {})
                if isinstance(psGroup, dict):
                    geGroup = psGroup.get("geGroup", {})
                    if isinstance(geGroup, dict):
                        xvGroup = geGroup.get("xvGroup", [])

                        if isinstance(xvGroup, dict):
                            xvGroup = [xvGroup]

                        if isinstance(xvGroup, list):
                            if lxGroup.get("lx", "") and geGroup.get("ge", ""):
                                transformed_data.append(
                                    {
                                        "input": lxGroup.get("lx", ""),
                                        "output": {
                                            "definition": geGroup.get("ge", "")
                                            if "ge" in geGroup
                                            else "",
                                            "etymology": lxGroup.get("etGroup", {}).get(
                                                "et", ""
                                            )
                                            if "et" in lxGroup.get("etGroup", {})
                                            else "",
                                            "synonym": psGroup.get("sy", {})
                                            if "sy" in psGroup
                                            else "",
                                        },
                                    }
                                )

                            for entry in xvGroup:
                                xv = entry.get("xv", "")
                                xe = entry.get("xe", "")
                                if xv and xe:
                                    transformed_data.append({"input": xv, "output": xe})
    print(f"Données transformées: {transformed_data}")  # Débogage
    return transformed_data


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
        wolof.append(str(line['input']))
        if line['output'] is not None:
            if isinstance(line['output'], dict) and 'definition' in line['output']:
                french.append(str(line['output']['definition']))
            else:
                french.append(str(line['output']))
        else:
            french.append(None)  

    if len(french) != len(wolof):
        raise ValueError('The number of french and wolof sentences are not equal')

    ds = Dataset.from_dict({"wolof": wolof, "french": french})
    return ds

async def main():
    input_file = 'word.txt'
    output_file = '../data/dataset.jsonl'
    delay = 1

    await create_jsonl_from_words(input_file, output_file, delay)

    ds = process_jsonl_to_dataset(output_file)

    dataset_dict = ds.train_test_split(test_size=0.2)

    dataset_dict.push_to_hub("jolof")   # Push to the hub

if __name__ == "__main__":
    asyncio.run(main())