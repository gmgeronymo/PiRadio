/*
test_RED.c
2015-11-18
Public Domain
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <unistd.h>

#include <pigpiod_if2.h>

#include "RED.h"

/*

REQUIRES

A rotary encoder contacts A and B connected to separate GPIO and
the common contact connected to Pi ground.

TO BUILD

gcc -Wall -pthread -o RED test_RED.c RED.c -lpigpiod_if2

TO RUN

sudo pigpiod # if the daemon is not already running

./RED -aGPIO -bGPIO

For option help

./RED -?

*/

void fatal(char *fmt, ...)
{
   char buf[128];
   va_list ap;

   va_start(ap, fmt);
   vsnprintf(buf, sizeof(buf), fmt, ap);
   va_end(ap);

   fprintf(stderr, "%s\n", buf);

   fflush(stderr);

   exit(EXIT_FAILURE);
}

void usage()
{
   fprintf(stderr, "\n" \
      "Usage: RED [OPTION] ...\n" \
      "   -a value, gpio A, 0-31,                  default None\n" \
      "   -b value, gpio B, 0-31,                  default None\n" \
      "   -m value, mode, 0=DETENT, 1=STEP         default DETENT\n" \
      "   -g value, glitch filter setting, 0-5000, default 1000\n" \
      "   -s value, run seconds, >=0 (0=forever),  default 0\n" \
      "   -h string, host name,                    default NULL\n" \
      "   -p value, socket port, 1024-32000,       default 8888\n" \
      "EXAMPLE\n" \
      "RED -a10 -b12\n" \
      "   Read a rotary encoder connected to GPIO 10/12.\n\n");
}

int optGpioA = -1;
int optGpioB = -1;
int optGlitch = 1000;
int optSeconds = 0;
int optMode = RED_MODE_DETENT;
char *optHost   = NULL;
char *optPort   = NULL;

static uint64_t getNum(char *str, int *err)
{
   uint64_t val;
   char *endptr;

   *err = 0;
   val = strtoll(str, &endptr, 0);
   if (*endptr) {*err = 1; val = -1;}
   return val;
}

static void initOpts(int argc, char *argv[])
{
   int opt, err, i;

   while ((opt = getopt(argc, argv, "a:b:m:g:s:h:p:")) != -1)
   {
      switch (opt)
      {
         case 'a':
            i = getNum(optarg, &err);
            if ((i >= 0) && (i <= 31)) optGpioA = i;
            else fatal("invalid -a option (%s)", optarg);
            break;

         case 'b':
            i = getNum(optarg, &err);
            if ((i >= 0) && (i <= 31)) optGpioB = i;
            else fatal("invalid -b option (%s)", optarg);
            break;

         case 'm':
            i = getNum(optarg, &err);
            if ((i >= 0) && (i <= 1)) optMode = i;
            else fatal("invalid -m option (%s)", optarg);
            break;

         case 'g':
            i = getNum(optarg, &err);
            if ((i >= 0) && (i <= 5000)) optGlitch = i;
            else fatal("invalid -g option (%s)", optarg);
            break;

         case 's':
            i = getNum(optarg, &err);
            if (i >= 0) optSeconds = i;
            else fatal("invalid -s option (%s)", optarg);
            break;

         case 'h':
            optHost = malloc(sizeof(optarg)+1);
            if (optHost) strcpy(optHost, optarg);
            break;

         case 'p':
            optPort = malloc(sizeof(optarg)+1);
            if (optPort) strcpy(optPort, optarg);
            break;

        default: /* '?' */
           usage();
           exit(-1);
        }
    }
}


void cbf(int pos)
{
   printf("%d\n", pos);
}

int main(int argc, char *argv[])
{
   int pi;
   RED_t *renc;

   initOpts(argc, argv);

   if ((optGpioA < 0) || (optGpioB < 0) || (optGpioA == optGpioB))
   {
      fprintf(stderr, "You must specify gpioA and gpioB.\n");
      exit(0);
   }

   pi = pigpio_start(optHost, optPort); /* Connect to Pi. */

   if (pi >= 0)
   {
      renc = RED(pi, optGpioA, optGpioB, optMode, cbf);
      RED_set_glitch_filter(renc, optGlitch);

      if (optSeconds) sleep(optSeconds);
      else while(1) sleep(60);

      RED_cancel(renc);

      pigpio_stop(pi);
   }
   return 0;
}

