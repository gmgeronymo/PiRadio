#!/usr/bin/env python
# PiRadio
# Radio Web usando mplayer e pigpiod

# funcao: inicializa lista de playlists
# parametros: nenhum
# retorno: nenhum
def IniciaListaPlaylists():
    global Playlists
    global NumeroPlaylists

    # playlist 1: Band News FM RJ
    Playlists.append("https://evpp.mm.uol.com.br/band/bandnewsfm_rj/playlist.m3u8")

    # playlist 2: Band News FM SP
    Playlists.append("https://evpp.mm.uol.com.br/band/bandnewsfm_sp/playlist.m3u8")

    # playlist 3: Band News FM CWB
    Playlists.append("https://evpp.mm.uol.com.br/band/bandnewsfm_ctb/playlist.m3u8")

    # playlist 4: .1 FM Classic Rock
    Playlists.append("http://yp.shoutcast.com/sbin/tunein-station.pls?id=1807142")

    NumeroPlaylists=4
    return

# funcao: toca playlist selecionada
# parametros: numero da playlist escolhida
# retorno: nenhum
def TocaPlaylist(PEscolhida):
    global Playlists
    global ComandoMPlayer

    os.system("pkill -f mplayer")
    ComandoPlaylist = ComandoMplayer + Playlists[PEscolhida]

    # inicia processo e direciona stdout para /dev/null
    FNULL = open(os.devnull,'w')
    args = shlex.split(ComandoPlaylist)
    InterfaceMPlayer = subprocess.Popen(args, shell=False, stdin=subprocess.PIPE, stdout=FNULL, stderr=subprocess.STDOUT)
    #InterfaceMPlayer = subprocess.Popen(args)
    return


# funcao: cria arquivo de controle do MPlayer
# parametros: nenhum
# retorno: nenhum
def CriaArquivoControle():
    #se arquivo ja existe, nada e feito
    if (os.path.exists(CaminhoArquivoControle)):
        return
    try:
        os.mkfifo(CaminhoArquivoControle)
    except:
        print "Falha ao criar arquivo de controle."
        exit(1)

# funcao de callback botao on/off
def callback_on_off(gpio, level, tick):
    global status
    global pid
    global url
    global PlaylistEscolhida
    if (pi.read(10) != status):
        # mudanca de status
        status = pi.read(10)
        if (status == 0):
            os.system("pkill -f mplayer")
        else:
            TocaPlaylist(PlaylistEscolhida)

# funcao de callback botao play/pause
def callback_play_pause(gpio, level, tick):
    os.system('echo "pause" > '+CaminhoArquivoControle)

# funcao de callback do rotary encoder 1
def rotary1_callback(way):
    global PlaylistEscolhida
    global NumeroPlaylists

    PlaylistEscolhida += way

    if (PlaylistEscolhida >= NumeroPlaylists) :
        PlaylistEscolhida = 0

    if (PlaylistEscolhida < 0) :
        PlaylistEscolhida = NumeroPlaylists - 1
    # salva playlist no arquivo temporario
    os.system('echo '+str(PlaylistEscolhida)+' > '+CaminhoUltimaPlaylist)
    TocaPlaylist(PlaylistEscolhida)

# funcao principal do programa
if __name__ == "__main__":

    import os
    import signal
    import time
    import subprocess
    import shlex
    import pigpio 
    import rotary_encoder

    # variaveis globais 
    #ComandoMplayer = "mplayer -ao alsa -srate 48000 -af pan=1:1 -input file=/tmp/ControleRadio -slave -playlist "
    ComandoMplayer = "mplayer -input file=/tmp/ControleRadio -slave -playlist "
    CaminhoArquivoControle = "/tmp/ControleRadio"
    CaminhoUltimaPlaylist = "/tmp/LastPlaylist"

    # variaveis das playlists
    Playlists=[]            # array com as playlists
    NumeroPlaylists = 0     # quantidade de playlists
    if (os.path.exists(CaminhoUltimaPlaylist)):
        PlaylistEscolhida = int(os.popen('cat '+CaminhoUltimaPlaylist).read())
    else :
        PlaylistEscolhida = 0   # indice da playlist escolhida

    # pinos de hardare
    enc1A = 27              # pino A do encoder 1
    enc1B = 22              # pino B do encoder 1
    pinOnOff = 10           # pino do rele on/off
    pinPlayPause = 17       # pino da chave do encoder 1

    # inicializacao da classe pigpiod
    pi = pigpio.pi()                        # inicializa pigpiod 
    pi.set_mode(pinOnOff, pigpio.INPUT)     # configura pino da chave on/off como input
    pi.set_glitch_filter(pinOnOff, 300)     # ativa filtro para o pino
    status = pi.read(pinOnOff)              # variavel de estado: 0 desligado, 1 ligado
    pi.set_mode(pinPlayPause, pigpio.INPUT) # configura botao do rotary encoder como input
    pi.set_pull_up_down(pinPlayPause, pigpio.PUD_UP)        # configura pino como pull-up
    pi.set_glitch_filter(pinPlayPause, 300) # ativa filtro para o pino

    # configura rotary encoder que seleciona radios
    decoder = rotary_encoder.decoder(pi, enc1A, enc1B, rotary1_callback)
    # configura funcao de callback para chave on/off
    cb1 = pi.callback(pinOnOff, pigpio.EITHER_EDGE, callback_on_off)
    # configura funcao de callback para botao do rotary encoder (play/pause)
    cb2 = pi.callback(pinPlayPause, pigpio.RISING_EDGE, callback_play_pause)

    IniciaListaPlaylists()                  # inicializa lista de playlists
    CriaArquivoControle()                   # cria arquivo de controle do MPlayer

    if (status == 1):
        TocaPlaylist(PlaylistEscolhida)
    # loop infinito: nao faz nada
    while True:
        signal.pause()


