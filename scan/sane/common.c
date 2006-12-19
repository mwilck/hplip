/************************************************************************************\

  common.c - common code for scl, pml, and soap backends

  (c) 2001-2006 Copyright Hewlett-Packard Development Company, LP

  Permission is hereby granted, free of charge, to any person obtaining a copy 
  of this software and associated documentation files (the "Software"), to deal 
  in the Software without restriction, including without limitation the rights 
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
  of the Software, and to permit persons to whom the Software is furnished to do 
  so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

  Contributing Authors: David Paschal, Don Welch, David Suffield 

\************************************************************************************/

#include <stdio.h>
#include <stdarg.h>
#include <syslog.h>
#include <string.h>
#include "common.h"

#define DEBUG_NOT_STATIC
#include "sanei_debug.h"

int bug(const char *fmt, ...)
{
   char buf[256];
   va_list args;
   int n;

   va_start(args, fmt);
   if ((n = vsnprintf(buf, 256, fmt, args)) == -1)
      buf[255] = 0;     /* output was truncated */
   syslog(LOG_WARNING, buf);
   DBG(2, buf);
   va_end(args);
   return n;
}

char *psnprintf(char *buf, int bufSize, const char *fmt, ...)
{
   va_list args;
   int n;

   buf[0] = 0;

   va_start(args, fmt);
   if ((n = vsnprintf(buf, bufSize, fmt, args)) == -1)
      buf[bufSize] = 0;     /* output was truncated */
   va_end(args);

   return buf;
}

unsigned long DivideAndShift( int line,
                              unsigned long numerator1,
                              unsigned long numerator2,
                              unsigned long denominator,
                              int shift )
{
    unsigned long remainder, shiftLoss = 0;
    unsigned long long result = numerator1;
    result *= numerator2;
    if( shift > 0 )
    {
        result <<= shift;
    }
    remainder = result % denominator;
    result /= denominator;
    if( shift < 0 )
    {
        shiftLoss = result & ( ( 1 << ( -shift ) ) - 1 );
        result >>= ( -shift );
    }
    return result;
}

void NumListClear( int * list )
{
    memset( list, 0, sizeof( int ) * MAX_LIST_SIZE );
}

int NumListIsInList( int * list, int n )
{
    int i;
    for( i = 1; i < MAX_LIST_SIZE; i++ )
    {
        if( list[i] == n )
        {
            return 1;
        }
    }
    return 0;
}

int NumListAdd( int * list, int n )
{
    if( NumListIsInList( list, n ) )
    {
        return 1;
    }
    if( list[0] >= ( MAX_LIST_SIZE - 1 ) )
    {
        return 0;
    }
    list[0]++;
    list[list[0]] = n;
    return 1;
}

int NumListGetCount( int * list )
{
    return list[0];
}

int NumListGetFirst( int * list )
{
    int n = list[0];
    if( n > 0 )
    {
        n = list[1];
    }
    return n;
}

void StrListClear( const char ** list )
{
    memset( list, 0, sizeof( char * ) * MAX_LIST_SIZE );
}

int StrListIsInList( const char ** list, char * s )
{
    while( *list )
    {
        if( !strcasecmp( *list, s ) )
        {
            return 1;
        }
        list++;
    }
    return 0;
}

int StrListAdd( const char ** list, char * s )
{
    int i;
    for( i = 0; i < MAX_LIST_SIZE - 1; i++ )
    {
        if( !list[i] )
        {
            list[i] = s;
            return 1;
        }
        if( !strcasecmp( list[i], s ) )
        {
            return 1;
        }
    }
    return 0;
}



