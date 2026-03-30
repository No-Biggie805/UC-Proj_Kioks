#include <stdio.h>
// #include <stdlib.h>
#include <stdint.h>
#include <fcntl.h> //controlo de ficheiros (open, O_RDWR)
#include <unistd.h> // Funcoes read/write/close
#include <termios.h> //em vez de hardware/uart.h no pico, configuracao da porta serie no linux

int main() {
  // 1. Abrir a porta serie (serial0, que e o atalho do rpi p/pinos 8 e 10)
  int uart0_filestream = open("/dev/serial0", O_RDWR | O_NOCTTY | O_NDELAY);
  if (uart0_filestream == -1) {
    printf("ERRO: Não foi possível abrir a porta UART. Ver permissões e o "
           "serial ativado!\n");
    return -1;
  }

  struct termios options;
  tcgetattr(uart0_filestream, &options);
  options.c_cflag = B115200 | CS8 | CLOCAL |
                    CREAD;  // 115200 baud, 8 bits, ignora modem, ativa leitura
  options.c_iflag = IGNPAR; // ignorar erros de paridade
  options.c_oflag = 0;
  options.c_lflag =
      0; // Modo "Raw" (lê os bytes puros, sem processar como texto)
  tcflush(uart0_filestream, TCIFLUSH);

  printf("a executar o TF02-Pro em C..\n");

  uint8_t buffer[9]; //9 bytes, palavras de 8 bits cada [ver a tabela]
  // uint8_t *test;

  while (1) {
    // if()

    // Lê 1 byte para tentar encontrar o primeiro 0x59
    if (read(uart0_filestream, &buffer[0], 1) == 1 &&
        buffer[0] == 0x59) { // 0x59 que em hex para ASCII => 'Y'
      // Se encountrou, ver o próximo a ver se também será 0x59 [byte de check]
      if (read(uart0_filestream, &buffer[1], 1) == 1 && buffer[1] == 0x59) {
        // Encontramos o cabeçalho, agora ler os restantes bytes
        int bytes_lidos = read(uart0_filestream, &buffer[2], 7);

        // chegou ao numero máximo de bytes

        // iniciar os checksums
        if (bytes_lidos == 7) {
          // calcular os checksums
          uint8_t checksum_calculado = 0;
          for (int i = 0; i < 8; i++) {
            checksum_calculado += buffer[i];
          }
          // se o checksum bater certo os dados sao validos:
          if (checksum_calculado == buffer[8]) {
            //calcular a distância e a força do sinal: (High * 256 | LOW)
            uint16_t distância_sinal = buffer[3] << 8 | buffer[2]; 
            uint16_t forca_sinal = buffer[5] << 8 | buffer[4];

            printf("Distancia: %d cm | forca do sinal: %d\n", distância_sinal,forca_sinal);
          }
        }
      }
    }
  }
  close(uart0_filestream);
  return 0;
}
