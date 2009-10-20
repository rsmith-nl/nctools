/* -*- c -*-
 * Time-stamp: <2009-10-20 21:25:13 rsmith>
 * 
 * readdxf.c
 * Copyright © 2009 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef NULL
#define NULL (void*)0
#endif

extern char *ftobuf(const char *name, long *l);


char *getline(char *f);
char *getarc(char *f);

int main(int argc, char *argv[])
{
	char *buf, *ptr, *lptr, *aptr, *eptr;
	long len;
#ifdef DEBUG
	fputs("Entering main.\n", stderr);
#endif
	if (argc!=2) {
		fputs("Usage: readdxf file\n", stderr);
		return 0;
	}

	buf = ftobuf(argv[1], &len);
	if (buf==NULL) {
#ifdef DEBUG
		fputs("Error reading input file.\n", stderr);
#endif
		return 1;
	}
#ifdef DEBUG
		fputs("Input file read into buffer.\n", stderr);
#endif

	/* Go to the ENTITIES section */
	ptr = strstr(buf, "ENTITIES");
	if (ptr==NULL) {
		fputs("No ENTITIES section in file.\n", stderr);
		return 2;
	}
	ptr += strlen("ENTITIES");
#ifdef DEBUG
		fputs("Found ENTITIES section.\n", stderr);
#endif
	/* Get the corresponding ENDSEC */
	eptr = strstr(ptr, "ENDSEC");
	if (eptr==NULL) {
		fputs("No ENDSEC for ENTITIES section in file.\n", stderr);
		return 3;
	}
#ifdef DEBUG
		fputs("Found ENDSEC for ENTITIES section.\n", stderr);
#endif
	lptr = ptr;
	while (lptr<eptr && lptr!=NULL && aptr<eptr && aptr!=NULL) {
		lptr = strstr(lptr, "LINE");
		aptr = strstr(aptr, "ARC");
		if (lptr<aptr) {
			lptr = getline(lptr);
			aptr = getarc(aptr);
		} else {
			aptr = getarc(aptr);
			lptr = getline(lptr);
		}
}

	return 0;
}

char *getline(char *f) {
	char *p = f, *e;
	int rv, l;
	float x1, y1, x2, y2;
	if (p==NULL) return NULL;
	p += 4;

	e = strstr(p, " 10");
	if (e==NULL) return p;
	p = e+3;
	x1 = strtof(p, &e);
	if (p==e) return p;

	e = strstr(p, " 20");
	if (e==NULL) return p;
	p = e+3;
	y1 = strtof(p, &e);
	if (p==e) return p;

	e = strstr(p, " 11");
	if (e==NULL) return p;
	p = e+3;
	x2 = strtof(p, &e);
	if (p==e) return p;

	e = strstr(p, " 21");
	if (e==NULL) return p;
	p = e+3;
	y2 = strtof(p, &e);
	if (p==e) return p;
	
	printf("Found line segment from (%g,%g) to (%g,%g)\n", x1,y1,x2,y2);

	return p;
}

char *getarc(char *f) {
	char *p = f, *e;
	int rv, l;
	float x1, y1, r, a1, a2;
	if (p==NULL) return NULL;
	p += 4;

	e = strstr(p, " 10");
	if (e==NULL) return p;
	p = e+3;
	x1 = strtof(p, &e);
	if (p==e) return p;

	e = strstr(p, " 20");
	if (e==NULL) return p;
	p = e+3;
	y1 = strtof(p, &e);
	if (p==e) return p;

	e = strstr(p, " 40");
	if (e==NULL) return p;
	p = e+3;
	r = strtof(p, &e);
	if (p==e) return p;

	e = strstr(p, " 50");
	if (e==NULL) return p;
	p = e+3;
	a1 = strtof(p, &e);
	if (p==e) return p;
	
	e = strstr(p, " 51");
	if (e==NULL) return p;
	p = e+3;
	a2 = strtof(p, &e);
	if (p==e) return p;
	
	printf("Found arc center (%g,%g) radius %g from %g° to %g°.\n", 
	       x1,y1,r,a1,a2);

	return p;
}
/* EOF readdxf.c */
