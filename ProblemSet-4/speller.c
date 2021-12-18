#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <strings.h>
#include <string.h>
#include <ctype.h>
#include "dictionary.h"

typedef struct node {
    char word[LENGTH + 1];
    struct node *next;
}
node;

const unsigned int N = 17000;
int fsize = 0;

node *table[N];

bool check(const char *word) {
    unsigned int hash_code = 0;
    hash_code = hash(word);
    for (node *tmp = table[hash_code]; tmp != NULL; tmp = tmp->next) {
        if (strcasecmp(tmp->word, word) == 0) {
            return true;
        }
    }
    return false;
}

unsigned int
hash(const char *word)

{
    unsigned int hash = 5381;
    int c;
    while ((c = *word++)) {
        if (isupper(c)) {
            c = c + 32;
        }
        hash = ((hash << 5) + hash) + c;
    }
    return hash % N;
}

bool load(const char *dictionary) {
    char words[46];
    int hash_code = 0;

    FILE *infile = fopen(dictionary, "r");
    if (infile == NULL) {
        return false;
    }

    while (fscanf(infile, "%s", words) != EOF) {
        node *n = malloc(sizeof(node));
        if (n == NULL) {
            return false;
        }

        strcpy(n->word, words);
        hash_code = hash(n->word);
        if (table[hash_code] == NULL) {
            table[hash_code] = n;
            n->next = NULL;
        }
        else {
            n->next = table[hash_code];
            table[hash_code] = n;
        }
        fsize++;
    }
    fclose(infile);
    return true;
}

unsigned int
size(void) {
    return fsize;
}

bool unload(void) {
    for (int i = 0; i < N; i++) {
        node *tmp = NULL;
        node *cursor = NULL;
        cursor = table[i];
        while (cursor != NULL) {
            tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
    }
    return true;
}
