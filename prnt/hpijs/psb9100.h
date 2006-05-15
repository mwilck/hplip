/*****************************************************************************\
  djgenericvip.h : Interface for the generic VIP printer class

  Copyright (c) 2001 - 2006, Hewlett-Packard Co.
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


#ifndef APDK_PS_B9100_H
#define APDK_PS_B9100_H

APDK_BEGIN_NAMESPACE

//PSB9100
//!
/*!
\internal
******************************************************************************/
class PSB9100 : public DJGenericVIP
{
public:
    PSB9100 (SystemServices* pSS, BOOL proto = FALSE) : DJGenericVIP (pSS, proto)
    {
        for (int i = 0; i < (int) ModeCount; i++)
        {
            if (pMode[i]->ResolutionX[0] == 300)
            {
                pMode[i]->BaseResX       =
                pMode[i]->BaseResY       = 
                pMode[i]->ResolutionX[0] =
                pMode[i]->ResolutionY[0] = 600;
                pMode[i]->medium         = mediaAuto;
            }
            else
            {
                pMode[i]->BaseResX       =
                pMode[i]->BaseResY       = 
                pMode[i]->ResolutionX[0] =
                pMode[i]->ResolutionY[0] = 1200;
                pMode[i]->medium         = mediaAuto;
                if (pMode[i]->medium == mediaHighresPhoto)
                {
                    pMode[i]->medium     = mediaGlossy;
                }
            }
        }
    }

    virtual BOOL FullBleedCapable (PAPER_SIZE ps, FullbleedType  *fbType, float *xOverSpray, float *yOverSpray,
                                   float *fLeftOverSpray, float *fTopOverSpray)
    {
		*xOverSpray = (float) 0.216;
		*yOverSpray = (float) 0.149;
		if (fLeftOverSpray)
			*fLeftOverSpray = (float) 0.098;
		if (fTopOverSpray)
			*fTopOverSpray  = (float) 0.051;

		*fbType = fullbleed4EdgeAllMedia;

        return TRUE;
    }
	virtual PAPER_SIZE MandatoryPaperSize ()
    {
        return UNSUPPORTED_SIZE;
    }
    virtual BOOL GetMargins (PAPER_SIZE ps, float *fMargins)
    {
        fMargins[0] = (float) 0.125;
        fMargins[1] = (float) 0.125;
        fMargins[2] = (float) 0.125;
        fMargins[3] = (float) 0.125;
        return TRUE;
    }
private:
	virtual void AdjustModeSettings (BOOL bDoFullBleed, MEDIATYPE ReqMedia,
									 MediaType *medium, Quality *quality)
    {
    }

}; //PSB9100

#if defined(APDK_DJGENERICVIP) && defined (APDK_DJ9xxVIP)
//! PSB9100Proxy
/*!
******************************************************************************/
class PSB9100Proxy : public PrinterProxy
{
public:
    PSB9100Proxy() : PrinterProxy(
        "PSB9100",                       // family name
        "Photosmart Pro B9100\0"
    ) {m_iPrinterType = ePSB9100;}
    inline Printer* CreatePrinter(SystemServices* pSS) const { return new PSB9100(pSS); }
	inline PRINTER_TYPE GetPrinterType() const { return ePSB9100;}
	inline unsigned int GetModelBit() const { return 0x80;}
};
#endif

APDK_END_NAMESPACE

#endif  // APDK_PS_B9100_H
