#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <unistd.h>

#include "controller.h"

extern struct cntrl *initControl() {
  struct cntrl *control;
  int key_in, key_out;
  
  control = (struct cntrl *) malloc(sizeof(struct cntrl));

  key_out = 4000 + (int)getuid();
  key_in = key_out + 10000;

  if((control->shmid_in = shmget((key_t)key_in, SHM_BUF_SIZE, SHM_PERM)) < 0) {
    perror("shmget");
    exit(1);
  }
  if((control->shmid_out = shmget((key_t)key_out, SHM_BUF_SIZE, SHM_PERM)) < 0) {
		perror("shmget");
		exit(1);
  }
  if((control->shm_in = shmat(control->shmid_in, NULL, 0)) == (char *) -1) {
    perror("shmat");
    exit(1);
  }
  if((control->shm_out = shmat(control->shmid_out, NULL, 0)) == (char *) -1) {
    perror("shmat");
    exit(1);
  }
  
  return control;
}

extern void endControl(struct cntrl *control) {
  struct shmid_ds   ds;

  shmctl(control->shmid_in, IPC_RMID, &ds);
  shmctl(control->shmid_out, IPC_RMID, &ds);
}
  
extern char *sendMessage(struct cntrl *control, char *message) {
  char *reply;
  reply = (char *) malloc(64);
  
  if(message[0] != '\0') {
    strcpy(control->shm_out, message);
    while(control->shm_in[0] == '\0') usleep(1);
    strcpy(reply, control->shm_in);
    control->shm_out[0] = '\0';
    return reply;
  } else return "";
}
