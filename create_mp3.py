import sys
import os


def get_dir_file_names(path):
    file_list = os.listdir(path)
    return file_list


def get_path(argv):
    if len(argv) <= 1:
        return './'
    else:
        return argv[1]


def get_voice(argv):
    vs = ['Alex' 'Alice', 'Alva', 'Amelie', 'Anna', 'Carmit',
          'Damayanti', 'Daniel', 'Diego', 'Ellen', 'Felipe', 'Fiona',
          'Fred', 'Ioana', 'Joana', 'Jorge', 'Juan', 'Kanya', 'Karen',
          'Kyoko', 'Laura', 'Lekha', 'Luca', 'Luciana', 'Maged', 'Mariska', 'Mei-',
          'Melina', 'Milena', 'Moira', 'Monica', 'Nora', 'Paulina', 'Rishi',
          'Samantha', 'Sara', 'Satu', 'Sin-ji', 'Tessa', 'Thomas', 'Ting-',
          'Veena', 'Victoria', 'Xander', 'Yelda', 'Yuna', 'Yuri', 'Zosia', 'Zuzana']

    if len(argv) <= 2:
        return 'Alex'
    else:
        if argv[2] in vs:
            return argv[2]
        else:
            return 'Alex'


def get_speed(argv):
    if len(argv) <= 3:
        return '175'
    else:
        return argv[3]


def check(argv):
    if len(argv) == 1:
        sys.exit("Invalid Arguments")
    if argv[1] == '?':
        os.system("say -v '?'")
        exit()


def main(argv):
    check(argv)
    path = get_path(argv)
    voice = get_voice(argv)
    speed = get_speed(argv)

    file_list = get_dir_file_names(path)

    count = 0
    for file in file_list:
        file_full_path = path+'/'+file
        file_aiff = path + '/' + file + ".aiff"
        file_mp3 = path + '/' + file + ".mp3"

        print(file + ' | ' + str(int(count/len(file_list)*100)))

        os.system("say -v " + voice + " -r " + speed +
                  " -o " + file_aiff + "  < " + file_full_path)
        os.system("lame -m m " + file_aiff + " " + file_mp3)
        os.system("rm " + file_aiff)

        count += 1


if __name__ == "__main__":
    main(sys.argv)
