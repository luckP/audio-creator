# audio-creator

This small python script allows you to create mp3 audios from text documents. Mac only.

## To run the script use the command below:

    python3 create_mp3.py <DIRECTORY WITH YOU TEXT FILES>

## If you want to change the language, pass the voice name with the language you want to use. By default, the voice used is Alex's. As shown in the example below.

    python3 create_mp3.py ./test-audio Alex

## To view the voices that have been installed, follow the example below.

    python3 create_mp3.py '?'

## Finally, you can change the reading speed, by default it is set to 150. As shown in the example:

    python3 create_mp3.py ./test-audio Alex 200
