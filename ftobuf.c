/* -*- c -*-
 * Time-stamp: <2009-10-20 20:49:05 rsmith>
 * 
 * ftobuf.c
 * Copyright © 2009 R.F. Smith <rsmith@xs4all.nl>. 
 * All rights reserved.
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

#ifndef NULL
#define NULL ((void*)0)
#endif

/* ftobuf - reads a file into a memory buffer.
 * name: name of a file.
 * l: returns the size of the buffer, or a negative error number.
 * Returns a pointer to a malloc-ed buffer containing the file.
 */
char *ftobuf(const char *name, long *l)
{
        char *b = NULL;
        FILE *f;
	long bl = 0;
        assert(name != NULL);
        f = fopen(name, "r");
        if (f == NULL) {
		if (l!=NULL) {*l = -1;}
		return NULL;
	}
        fseek(f, 0, SEEK_END);
        bl = ftell(f);
        rewind(f);
        if (bl == -1) {
                fclose(f);
		if (l!=NULL) {*l = -2;}
		return NULL;
        }
        b = malloc(bl+1); /* for an extra zero at the end. */
	if (b == NULL) {
                fclose(f);
		if (l!=NULL) {*l = -3;}
		return NULL;
	}
        fread(b, bl, 1, f);
        if (ferror(f)) {
                fclose(f);
		free(b);
		if (l!=NULL) {*l = -4;}
		return NULL;
        }
	b[bl] = 0;
        if (l!=NULL) {
                *l = bl;
        }
        fclose(f);
        return b;
}

/* EOF ftobuf.c */
