import os, csv

def insertTimeIntoFileName(inputDirectory, DataCsv):
    if not os.path.exists(os.path.join(inputDirectory, DataCsv+".csv")):
        print(f"A megadott CSV fájl nem létezik: {DataCsv}")
        exit(1)

    if not os.path.exists(inputDirectory) or not os.path.exists(os.path.join(inputDirectory, DataCsv)):
        print(f"A megadott könyvtár nem létezik: {inputDirectory}")
        exit(1)
    clipsDirectory = os.path.join(inputDirectory, DataCsv)

    csv_path = os.path.join(inputDirectory, DataCsv + ".csv")
    dictClips = {}
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dictClips[row['id']] = row['created_at']

    for file_name in os.listdir(clipsDirectory):
        if str.isnumeric(file_name[0:4]):
            continue
        file_path = os.path.join(clipsDirectory, file_name)
        if os.path.isfile(file_path):
            clip_id = file_name[file_name.index('[')+1:-5]
                
            if clip_id in dictClips:
                created_at = dictClips[clip_id]
                time_part = created_at[5:7] + created_at[8:10] + '-' + created_at[11:13] + created_at[14:16]
                new_file_name = f"{time_part} {file_name}"
                new_file_path = os.path.join(clipsDirectory, new_file_name)
                os.rename(file_path, new_file_path)
                print(f"{new_file_name}")
            else:
                print(f"Nincs adat a fájlhoz: {file_name}")

if __name__ == "__main__":
    month = "11"
    insertTimeIntoFileName("d:/dev/ClipsToVideoMaker/Clips", month)