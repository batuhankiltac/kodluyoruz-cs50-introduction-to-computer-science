#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "bmp.h"

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: ./resize f infile outfile\n");
        return 1;
    }

    float f;
    sscanf(argv[1], " %f", &f);

    if (f > 100.0 || f < 0.0) {
        fprintf(stderr, "Usage: ./resize f infile outfile\n");
        return 1;
    }

    char *infile = argv[2];
    char *outfile = argv[3];

    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL) {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 1;
    }

    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL) {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 1;
    }

    BITMAPFILEHEADER bf, bfOut;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);
    bfOut = bf;

    BITMAPINFOHEADER bi, biOut;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);
    biOut = bi;

    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    biOut.biWidth = floor(bi.biWidth * f);
    biOut.biHeight = floor((bi.biHeight > 0 ? -bi.biHeight : bi.biHeight) * f);
    int paddingOut = (4 - biOut.biWidth * sizeof(RGBTRIPLE) % 4) % 4;

    biOut.biSizeImage =
        ((sizeof(RGBTRIPLE) * biOut.biWidth) +
         paddingOut) *
        abs(biOut.biHeight);

    bfOut.bfSize = biOut.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    fwrite(&bfOut, sizeof(BITMAPFILEHEADER), 1, outptr);
    fwrite(&biOut, sizeof(BITMAPINFOHEADER), 1, outptr);

    int cols = abs(bi.biHeight);
    int i, j, k, l, indJ, indI;
    RGBTRIPLE inScanLines[cols][bi.biWidth];
    if (bi.biHeight < 0) {
        for (i = 0; i < abs(bi.biHeight); i++) {
            for (j = 0; j < bi.biWidth; j++) {
                fread(&(inScanLines[i][j]), sizeof(RGBTRIPLE), 1, inptr);
            }
            fseek(inptr, padding, SEEK_CUR);
        }
    }
    else {
        for (i = bi.biHeight - 1; i >= 0; i--) {
            for (j = 0; j < bi.biWidth; j++) {
                fread(&(inScanLines[i][j]), sizeof(RGBTRIPLE), 1, inptr);
            }
            fseek(inptr, padding, SEEK_CUR);
        }
    }
    cols = abs(biOut.biHeight);
    RGBTRIPLE outScanLines[cols][biOut.biWidth];

    for (i = 0; i < abs(bi.biHeight); i++) {
        indI = floor(i * f);
        for (j = 0; j < bi.biWidth; j++) {
            indJ = ceil(f * j);
            outScanLines[indI][indJ] = inScanLines[i][j];
            for (k = floor(f) - 1; k > 0; k--) {
                outScanLines[indI][indJ + k] = inScanLines[i][j];
            }
        }
        for (l = floor(f) - 1; l > 0; l--) {
            for (j = 0; j < bi.biWidth; j++) {
                indJ = ceil(f * j);
                outScanLines[indI + l][indJ] = inScanLines[i][j];
                for (k = floor(f) - 1; k > 0; k--) {
                    outScanLines[indI + l][indJ + k] = inScanLines[i][j];
                }
            }
        }
    }

    for (i = 0; i < abs(biOut.biHeight); i++) {
        for (j = 0; j < biOut.biWidth; j++) {
            fwrite(&outScanLines[i][j], sizeof(RGBTRIPLE), 1, outptr);
        }
        for (k = 0; k < paddingOut; k++) {
            fputc(0x00, outptr);
        }
    }
    fclose(inptr);
    fclose(outptr);
    return 0;
}
