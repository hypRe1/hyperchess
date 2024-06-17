import csv

with open("countries.csv") as csvfile:
    with open("countriesnew.csv", "w") as csvfile2:
        spamreader = csv.reader(csvfile)
        spamwriter = csv.writer(csvfile2)
        for row in spamreader:
            emoji = row[0]
            code = row[2]
            name = row[3]
            image = row[-2]
            image2 = row[-1]

            image3 = (
                "https://upload.wikimedia.org/wikipedia/commons/"
                + image2.split("thumb/")[-1][:5]
                + image.split("File:")[-1]
            )
            if name:
                spamwriter.writerow((code, name, emoji, image3))
                print(code, name, emoji, image3)

# https://en.wikipedia.org/wiki/File:Emojione_1F1EC-1F1E7.svg
# https://upload.wikimedia.org/wikipedia/commons/8/83/Emojione_1F1EC-1F1E7.svg
# https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Emojione_1F1EC-1F1E7.svg/32px-Emojione_1F1EC-1F1E7.svg.png

# https://en.wikipedia.org/wiki/File:Emojione_1F1EC-1F1E7.svg
# https://upload.wikimedia.org/wikipedia/commons/c/cc/Emojione_1F1EC-1F1E7.svg
# https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Emojione_1F1FF-1F1FC.svg/32px-Emojione_1F1FF-1F1FC.svg.png
# https://upload.wikimedia.org/wikipedia/commons/httpsEmojione_1F1FF-1F1FC.svg
