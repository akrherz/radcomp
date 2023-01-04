/********************************************************************
 * ucnids - NIDS decompression utility for data compressed with zlib
 *
 *   syntax: ucnids [options] ifile ofile
 *   ifile and ofile can be "-" to use standard input and output
 *   options: 
 *     none - output uncompressed product with NOAAPORT CCB
 *     -c   - output with standard WMO CCB
 *     -r   - output with strippped WMO CCB (RPS output)
 *     -w   - output with WXP-like WMO header
 *     -n   - output stripping header and leaving raw NIDS data
 ********************************************************************/
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <zlib.h>
#include <sys/stat.h>

void mkdirs( char *path ){
    int len;
    int i;

    len = strlen( path );

    for( i = 1; i < len-1; i++ ){
        if( path[i] == '/' ){
            path[i] = 0;
            mkdir( path, 0755 );
            path[i] = '/';
        }
    }
}

int main( int argc, char **argv ){
    FILE *ifile;
    FILE *ofile;
    unsigned char soh[101];
    unsigned char seq[101];
    unsigned char wmo[101];
    unsigned char awip[101];
    unsigned char inbuf[4000];
    const int inlen = 4000;
    unsigned int insize;
    unsigned char outbuf[10000];
    char str[40];
    z_stream zs;
    int out;
    int len;
    int iret;
    int off;
    int i;
    int verb;
    int wxp;
    int inbytes;
    int outbytes;
    int cmp;
    int check;
    int floc;

    verb = 0;
    out = 5;

    off = 0;
    while( 1 ){
        if( argc > 1 && !strcmp( argv[1+off], "-h" )){
            printf( "ucnids: inflates NIDS products (removes zlib compression)\n" );
            printf( "syntax: ucnids [opts] in out\n" );
            printf( "  -v verbose mode\n" );
            printf( "  -d debug mode\n" );
            printf( "  -c WMO CCB header on output\n" );
            printf( "  -w WMO header with asterisks on output\n" );
            printf( "  -n Raw NIDS data on output\n" );
            printf( "  -r Raw NIDS with WMO header on output\n" );
            exit(0);
        }
        else if( argc > 1 && !strcmp( argv[1+off], "-v" )){
            verb = 1;
            off++;
        }
        else if( argc > 1 && !strcmp( argv[1+off], "-d" )){
            verb = 2;
            off++;
        }
        else if( argc > 1+off && !strcmp( argv[1+off], "-c" )){
            out = 1;
            off++;
        }
        else if( argc > 1+off && !strcmp( argv[1+off], "-w" )){
            out = 2;
            off++;
        }
        else if( argc > 1+off && !strcmp( argv[1+off], "-n" )){
            out = 3;
            off++;
        }
        else if( argc > 1+off && !strcmp( argv[1+off], "-r" )){
            out = 4;
            off++;
        }
        else 
            break;
    }
    if( argc == 1+off || argv[1+off][0] == '-' )
        ifile = stdin;
    else
        ifile = fopen( argv[1+off], "r" );
    if( ifile == NULL ) exit( 1 );

    if( argc < 3+off || argv[2+off][0] == '-' )
        ofile = stdout;
    else {
        mkdirs( argv[2+off] );
        ofile = fopen( argv[2+off], "w" );
        if( !ofile ) exit( 1 );
    }

    fgets( soh, 100, ifile );
    /*
       Account for both raw input (0x01) and WXP input (**)
       */
    wxp = 0;
    off = 0;
    check = ((soh[0] << 8 + soh[1]) % 31);
    if( check == 0 ){
        off = strlen( soh );
        memcpy( inbuf, soh, off );
    }
    else if( soh[0] == '\n' ){
        fgets( soh, 100, ifile );
        len = strlen( soh )-7;
        memcpy( wmo, soh+3, len );
        wmo[len] = 0;
        fgets( awip, 100, ifile );
        wxp = 1;
    }
    else if( soh[0] == '*' ){
        len = strlen( soh )-7;
        memcpy( wmo, soh+3, len );
        wmo[len] = 0;
        fgets( awip, 100, ifile );
        wxp = 1;
    }
    else if( soh[0] == 0x01 ){
        fgets( seq, 100, ifile );
        fgets( wmo, 100, ifile );
        fgets( awip, 100, ifile );
    }

    iret = 0;
    cmp = 0;
    zs.total_out = 4000;

    for( i = 0; i < 1000 && (iret != Z_STREAM_END || zs.total_out == 4000); i++ ){
        /* 
           Read in a block of data
           */
        floc = ftell( ifile );
        insize = fread( inbuf+off, 1, inlen-off, ifile ); 
        if( verb == 2 ) fprintf( stderr, "Read: %X %d\n", floc, insize );
        if( off == 0 && insize == 0 ) break;
        inbytes+=insize;
        len = insize + off;
        /* 
           Check for 789C byte sequence denoting zlib compression
           If data are not compressed, pass through raw data
           */
        strcpy( str, "" );
        check = (((inbuf[0] << 8) + inbuf[1]) % 31);
        if( verb == 2 ) fprintf( stderr, "check %X %X %d\n", inbuf[0], inbuf[1], check );
        if( i == 0 && check != 0 ){
            if( wxp ){
                if( out == 1 ){
                    fwrite( "\001\r\r\n001\r\r\n", 1, 10, ofile );
                    fprintf( ofile, "%18.18s\r\r\n", wmo );
                }
                else if( out == 2 ){
                    fprintf( ofile, soh );
                    fprintf( ofile, awip );
                }
            }
            else {
                if( out == 1 ){
                    fprintf( ofile, soh );
                    fprintf( ofile, seq );
                    fprintf( ofile, wmo );
                    fprintf( ofile, awip );
                }
                else if( out == 2 ){
                    fprintf( ofile, "** %18.18s ***\n%s", wmo, awip );
                }
            }
            fwrite( inbuf, 1, insize, ofile );
            while(( insize = fread( inbuf, 1, inlen, ifile )) > 0 ){
                fwrite( inbuf, 1, insize, ofile );
            }
            exit( 0 );
        }
        if( inbuf[0] == 0x78 && inbuf[1] == 0xDA ){
            zs.avail_in = len;
            zs.avail_out = 10000;
            zs.next_in = inbuf;
            zs.next_out = outbuf;
            /*
               Check to see if 4000 byte block has been read and reinitialize
               */
            if( i == 0 || iret == Z_STREAM_END ){
                zs.zalloc = NULL;
                zs.zfree = NULL;
                inflateInit( &zs );
            }
            /*
               Inflate NIDS data
               */
            iret = inflate( &zs, Z_STREAM_END );
            if( iret == 0 ) strcpy( str, "OK" );
            if( iret == 1 ) strcpy( str, "END" );
            if( iret < 0 ) strcpy( str, "ERR" );
            cmp = 1;
            if( verb == 2 ) fprintf( stderr, "Inf: %s -- %d %d %d -- 10000 %d %d -- %2X %2X -- %2X %2X\n", 
                    str, len, zs.avail_in, zs.total_in, zs.avail_out, zs.total_out, 
                    inbuf[0], inbuf[1], outbuf[0], outbuf[1] );
            off = zs.avail_in;
            // If return bad, assume it's uncompressed with fake positive
            if( iret < 0 ){
                memcpy( outbuf, inbuf, len );
                zs.avail_out = 10000-len;
                cmp = 0;
                off = 0;
                if( verb == 2 ) fprintf( stderr, "Bad-Cpy: %d - %2X %2X\n", len, inbuf[0], inbuf[1] );
            }
        }
        else {
            memcpy( outbuf, inbuf, len );
            zs.avail_out = 10000-len;
            cmp = 0;
            off = 0;
            if( verb == 2 ) fprintf( stderr, "Cpy: %d - %2X %2X\n", len, inbuf[0], inbuf[1] );
        }
        /*  
            Process header data for first block
            WMO CCB output
            */
        if( i == 0 && out == 1 ){
            fwrite( "\001\r\r\n001\r\r\n", 1, 10, ofile );
            fwrite( outbuf+24, 1, 10000-zs.avail_out-24, ofile );
        } 
        /*
           WXP header output
           */
        else if( i == 0 && out == 2 ){
            fprintf( ofile, "** %18.18s ***\n%s", wmo, awip );
            fwrite( outbuf+54, 1, 10000-zs.avail_out-54, ofile );
        } 
        /*
           Raw NIDS output
           */
        else if( i == 0 && out == 3 ){
            fwrite( outbuf+54, 1, 10000-zs.avail_out-54, ofile );
            outbytes+=10000-zs.avail_out-54;
        } 
        /*
           Stripped WMO CCB output
           */
        else if( i == 0 && out == 4 ){
            fwrite( outbuf+24, 1, 10000-zs.avail_out-24, ofile );
        } 
        /*
           Raw output with NOAAPORT CCB
           */
        else {
            fwrite( outbuf, 1, 10000-zs.avail_out, ofile );
            outbytes+=10000-zs.avail_out;
        } 
        /*
           Move remaining data that still is compressed and prepared 
           for next inflate
           */
        if( verb == 2 ) printf( "move %d\n", off );
        if( verb ){
            if( str[0] )
                printf( "Block %d size: %d cmp: %s\n", i, len-off, str );
            else
                printf( "Block %d size: %d\n", i, len-off );
        }
        memcpy( inbuf, inbuf+len-off, off );
    }
    exit( 0 );
}
