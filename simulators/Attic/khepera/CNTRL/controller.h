#ifndef CONTROLLER_H
#define CONTROLLER_H


#include <sys/types.h>

#define SHM_BUF_SIZE  64
#define SHM_PERM      0600

struct cntrl {
	int shmid_in, shmid_out;
	char *shm_in, *shm_out;
};

extern struct cntrl *initControl(void);
extern void endControl(struct cntrl *control);
extern char *sendMessage(struct cntrl *control, char *message);


#endif
