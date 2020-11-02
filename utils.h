#ifndef _MY_UTILS_HR_
#define _MY_UTILS_HR_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "board-peripherals.h"

/**
 * Parses http GET header
 * data: the data to parse, lenData the length of the data
 * lenParameters: amount of space in each char array (assumes all are constant)
 * Returns number of parameters found (up to 3)
 * p1, p2, p3 will be filled with the parameters
 * eg:
 * int n = parseGetRequest("GET /acc/20", 11, LEN_PARAMETERS, &p1, &p2, &p3);
 * returns:
 * n = 2
 * p1 = "acc"
 * p2 = "20"
 * 
 * Note: the returned strings are not null terminated please ensure they are initialised to 0
 */
int parseGetRequest(const char *data, int lenData, int lenParameters, char *p1, char *p2, char *p3) {
    int num = 0;
	int slashCounter = 0;
	int index = 0;
	for (int i = 0; i < lenData; i++) {
		char c = data[i];
		if (c == '\0') break;
		if (c == '/' || index >= lenParameters) {
			slashCounter++;
			index = 0;
			continue;
		}
		if (c == ' ' && slashCounter > 0) break;
		if (slashCounter == 0) continue;
		if (slashCounter == 1) {
			p1[index] = c;
			num = 1;
		} else if (slashCounter == 2) {
			p2[index] = c;
			num = 2;
		} else if (slashCounter == 3) {
			p3[index] = c;
			num = 3;
		}
		index++;
	}
	return num;
}

bool startsWith(const char *pre, const char *str) {
    size_t lenpre = strlen(pre),
           lenstr = strlen(str);
    return lenstr < lenpre ? false : memcmp(pre, str, lenpre) == 0;
}

/**
 * returns if operation was successful, i.e. not equal to zero
 */ 
bool myAtoi(char *srcStirng, int *dest) {
	int val = atoi(srcStirng);
	if (val != 0) {
		*dest = val;
		return true;
	}
	return false;
}

#endif