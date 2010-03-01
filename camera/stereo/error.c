/*********************************************************************
/* error.c
/*
/* Error and warning messages, and system commands.
/*********************************************************************
*/


#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

#include "error.h"

/*********************************************************************
/* error
/* 
/* Prints an error message and dies.
/* 
/* INPUTS
/* 	exactly like printf
/*********************************************************************
*/

void error(char *fmt, ...)
{
	va_list args;

	va_start(args, fmt);
	fprintf(stderr, "Error: ");
	vfprintf(stderr, fmt, args);
	fprintf(stderr, "\n");
	va_end(args);
	exit(1);
}


/*********************************************************************
/* warning
/* 
/* Prints a warning message.
/* 
/* INPUTS
/* 	exactly like printf
/*********************************************************************
*/

void warning(char *fmt, ...)
{
	va_list args;

	va_start(args, fmt);
	fprintf(stderr, "Warning: ");
	vfprintf(stderr, fmt, args);
	fprintf(stderr, "\n");
	fflush(stderr);
	va_end(args);
}


/*********************************************************************
/* command
/* 
/* Invokes a shell command, using the "system" call.
/* 
/* INPUTS
/* 	exactly like printf
/*********************************************************************
*/

void command(char *fmt, ...)
{
	static char cmd[80];
	va_list args;

	va_start(args, fmt);
	vsprintf(cmd, fmt, args);
	system(cmd);
	va_end(args);
}
