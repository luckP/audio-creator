import sys
import os
import eyed3

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
        
def insert_info():
    print('Enter Title:')
    album = input()
    print('Enter Artist Name:')
    artist_name = input()
    
    return album, artist_name

def get_img_path(path, file_list):
    for file in file_list:
        if(file.endswith('.png')):
            return path + '/' + file
    return ''
    

def main(argv):
    check(argv)
    album, artist_name = insert_info()
    path = get_path(argv)
    voice = get_voice(argv)
    speed = get_speed(argv)

    file_list = get_dir_file_names(path)
    img_path = get_img_path(path, file_list)
    
    # READ ART IMAGE
    if img_path!='':
        print('would you like to generate mp4 file? yes(y)/no(N)')
        generate_mp4 = input()
        generate_mp4 = generate_mp4 == 'y'
        
        with open(img_path, 'rb',) as cover_art:
            artwork = cover_art.read()
    
    count = 0
    for file in file_list:
        if file.endswith('.png'):
            continue
        
        file_full_path = path+'/'+file
        file_aiff = path + '/' + file + ".aiff"
        file_mp3 = path + '/' + file + ".mp3"

        print(file + ' | ' + str(int(count/len(file_list)*100)))

        os.system("say -v " + voice + " -r " + speed +
                  " -o " + file_aiff + "  < " + file_full_path)
        os.system("lame -m m " + file_aiff + " " + file_mp3)
        os.system("rm " + file_aiff)
        
        # ADD ALBUM NAME AND ARTIST NAME
        audio = eyed3.load(file_mp3)
        audio.initTag()
        audio.tag.artist = artist_name
        audio.tag.album = album
        audio.tag.album_artist = artist_name
        audio.tag.title = album + ' - ' + file
        
        # ADD LYRICS
        # with open(file_full_path, 'r', encoding="utf8") as file:

        with open(file_full_path, 'rb') as f:
            lyrics = f.read().decode(errors='replace')


        audio.tag.lyrics.set(str(lyrics))
        
        # ADD ART IMAGE
        if img_path!='':
            audio.tag.images.set(3, artwork, "image/png")
        
        # GENERATE MP4 FILE
        if generate_mp4:
            os.system("ffmpeg -loop 1 -i "+ img_path +" -i "+ file_mp3 +" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "+path + '/' + file + ".mp4")

            
        audio.tag.save()

        count += 1


if __name__ == "__main__":
    main(sys.argv)
