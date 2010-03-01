#include <stdlib.h>
#include "controller.h"

#define PROMPT "> "
#define BUFFER_LENGTH SHM_BUF_SIZE


char *GetString(void);


int main() {
	struct cntrl *p;
	char *query, *reply;

	p = initControl();
	
	while(1) {
		printf(PROMPT);
		query = GetString();
		if(!strncmp(query, "exit", 4)) break;
		if(query[0]!='\0') {
			reply = sendMessage(p,query);
			printf(reply);
		}
	}
}


char *GetString(void) {
	char *line, ch;
	int i = 0;
	line = (char *) malloc(BUFFER_LENGTH + 1);
	while( (ch = getchar()) != '\n' ) {  
		*(line + i) = ch;
		i++;
		if( i == BUFFER_LENGTH ) break;
	}
	*(line + i) = '\0';
	return( line );
}

