/*****************************************************************************\
  colormatcher_open.cpp : Implimentation for the ColorMatcher_Open class

  Copyright (c) 1996 - 2002, Hewlett-Packard Co.
  All rights reserved.

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. Neither the name of Hewlett-Packard nor the names of its
     contributors may be used to endorse or promote products derived
     from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
  NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
  TO, PATENT INFRINGEMENT; PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
  OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
  ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
\*****************************************************************************/

#include "header.h"
#include "hptypes.h"
#include "colormatch.h"

#include "colormatcher_open.h"

APDK_BEGIN_NAMESPACE

ColorMatcher_Open::ColorMatcher_Open
(
    SystemServices* pSys,
    ColorMap cm,
    unsigned int DyeCount,
    unsigned int iInputWidth
) : ColorMatcher(pSys,cm, DyeCount,iInputWidth)
{  }

ColorMatcher_Open::~ColorMatcher_Open()
{ }


#define DOCALC(a, b, d)     a + ( ( ( (long)b - (long)a ) * d) >> 5)

/*
BYTE DOCALC(BYTE a, BYTE b, BYTE d)
{
    return a + ( ( ( (long)b - (long)a ) * d) >> 5);
}

BYTE NewCalc(BYTE color[8], BYTE diff_red, BYTE diff_green, BYTE diff_blue)
{
    int dr32 = diff_red - 32;
    int dg32 = diff_green - 32;
    int db32 = diff_blue - 32;

    int x;
    x = -(color[0] * db32 * dg32 * dr32 + color[1] * diff_blue * (32 - diff_red) * dg32 +
        color[2] * diff_green * (32 - diff_red) * db32 + color[3] * diff_blue * diff_green * dr32 -
        diff_red * (color[4] * db32 * dg32 + color[5] * diff_blue * (32 - diff_green) -
        diff_green * (color[6] * db32 - color[7] * diff_blue))) >> 15;
    return x;
}
*/

void ColorMatcher_Open::Interpolate
(
    const uint32_t *start,
    const unsigned long i,
    BYTE r,
    BYTE g,
    BYTE b,
    BYTE *blackout,
    BYTE *cyanout,
    BYTE *magentaout,
    BYTE *yellowout,
    HPBool firstPixelInRow
)
{
    static BYTE prev_red = 255, prev_green = 255, prev_blue = 255;
    static BYTE bcyan, bmagenta, byellow, bblack;

    if(firstPixelInRow || ( (prev_red != r) || (prev_green != g) || (prev_blue != b) ))
    {
        // update cache info
        prev_red = r;
        prev_green = g;
        prev_blue = b;

#ifdef  _WIN32_WCE
        long    cyan[8], magenta[8],yellow[8],black[8];
#else
        BYTE    cyan[8], magenta[8],yellow[8],black[8];
#endif

        uint32_t cValue = (*start);
        cyan[0]=GetCyanValue(cValue);
        magenta[0] = GetMagentaValue(cValue);
        yellow[0] = GetYellowValue(cValue);
        black[0] = GetBlackValue(cValue);

        cValue = *(start+1);
        cyan[1]=GetCyanValue(cValue);
        magenta[1] = GetMagentaValue(cValue);
        yellow[1] = GetYellowValue(cValue);
        black[1] = GetBlackValue(cValue);

        cValue = *(start+9);
        cyan[2]=GetCyanValue(cValue);
        magenta[2] = GetMagentaValue(cValue);
        yellow[2] = GetYellowValue(cValue);
        black[2] = GetBlackValue(cValue);

        cValue = *(start+10);
        cyan[3]=GetCyanValue(cValue);
        magenta[3] = GetMagentaValue(cValue);
        yellow[3] = GetYellowValue(cValue);
        black[3] = GetBlackValue(cValue);

        cValue = *(start+81);
        cyan[4]=GetCyanValue(cValue);
        magenta[4] = GetMagentaValue(cValue);
        yellow[4] = GetYellowValue(cValue);
        black[4] = GetBlackValue(cValue);

        cValue = *(start+82);
        cyan[5]=GetCyanValue(cValue);
        magenta[5] = GetMagentaValue(cValue);
        yellow[5] = GetYellowValue(cValue);
        black[5] = GetBlackValue(cValue);

        cValue = *(start+90);
        cyan[6]=GetCyanValue(cValue);
        magenta[6] = GetMagentaValue(cValue);
        yellow[6] = GetYellowValue(cValue);
        black[6] = GetBlackValue(cValue);

        cValue = *(start+91);
        cyan[7]=GetCyanValue(cValue);
        magenta[7] = GetMagentaValue(cValue);
        yellow[7] = GetYellowValue(cValue);
        black[7] = GetBlackValue(cValue);

        ////////////////this is the 8 bit 9cube operation /////////////
        BYTE diff_red = r & 0x1f;
        BYTE diff_green = g & 0x1f;
        BYTE diff_blue = b & 0x1f;

        bcyan   =   DOCALC( (DOCALC( (DOCALC( cyan[0], cyan[4], diff_red)), (DOCALC( cyan[2], cyan[6], diff_red)), diff_green)),
            (DOCALC( (DOCALC( cyan[1], cyan[5], diff_red)), (DOCALC( cyan[3], cyan[7], diff_red)), diff_green)),
            diff_blue);
        bmagenta =  DOCALC( (DOCALC( (DOCALC( magenta[0], magenta[4], diff_red)), (DOCALC( magenta[2], magenta[6], diff_red)), diff_green)),
            (DOCALC( (DOCALC( magenta[1], magenta[5], diff_red)), (DOCALC( magenta[3], magenta[7], diff_red)), diff_green)),
            diff_blue);
        byellow =   DOCALC( (DOCALC( (DOCALC( yellow[0], yellow[4], diff_red)), (DOCALC( yellow[2], yellow[6], diff_red)), diff_green)),
            (DOCALC( (DOCALC( yellow[1], yellow[5], diff_red)), (DOCALC( yellow[3], yellow[7], diff_red)), diff_green)),
            diff_blue);
        bblack  =   DOCALC( (DOCALC( (DOCALC( black[0], black[4], diff_red)), (DOCALC( black[2], black[6], diff_red)), diff_green)),
            (DOCALC( (DOCALC( black[1], black[5], diff_red)), (DOCALC( black[3], black[7], diff_red)), diff_green)),
            diff_blue);
/*
        BYTE xcyan, xmagenta, xyellow, xblack;

        xcyan = NewCalc(cyan, diff_red, diff_green, diff_blue);

        xmagenta = NewCalc(magenta, diff_red, diff_green, diff_blue);

        xyellow = NewCalc(yellow, diff_red, diff_green, diff_blue);

        xblack = NewCalc(black, diff_red, diff_green, diff_blue);

        ASSERT(bcyan == xcyan);
        ASSERT(bmagenta == xmagenta);
        ASSERT(byellow == xyellow);
        ASSERT(bblack == xblack);
*/
    }

    if(cyanout)
    {
        *(cyanout + i)    = bcyan;
    }

    if(magentaout)
    {
        *(magentaout + i) = bmagenta;
    }

    if(yellowout)
    {
        *(yellowout + i)  = byellow;
    }

    if(blackout)
    {
        *(blackout + i)   = bblack;
    }

}

APDK_END_NAMESPACE
