/*****************************************************************************\
  djgenericvip.h : Interface for the generic VIP printer class

  Copyright (c) 2001 - 2002, Hewlett-Packard Co.
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


#ifndef APDK_DJ_GENERIC_VIP_H
#define APDK_DJ_GENERIC_VIP_H

APDK_BEGIN_NAMESPACE

//DJGenericVIP
//!
/*!
\internal
******************************************************************************/
class DJGenericVIP : public DJ9xxVIP
{
public:
    DJGenericVIP (SystemServices* pSS, BOOL proto = FALSE);

    DRIVER_ERROR VerifyPenInfo ();
    virtual BOOL FullBleedCapable (PAPER_SIZE ps, FullbleedType  *fbType, float *xOverSpray, float *yOverSpray,
                                   float *fLeftOverSpray, float *fTopOverSpray);
	virtual BOOL UseGUIMode (PrintMode *pPrintMode);
	virtual PAPER_SIZE MandatoryPaperSize ();
    virtual PHOTOTRAY_STATE PhotoTrayEngaged (BOOL bQueryPrinter);
    //! Returns TRUE if a hagaki feed is present in printer.
    virtual BOOL HagakiFeedPresent(BOOL bQueryPrinter);

#ifdef APDK_AUTODUPLEX
    //!Returns TRUE if duplexer and hagaki feed (combined) unit is present in printer.

    virtual BOOL HagakiFeedDuplexerPresent(BOOL bQueryPrinter);
#endif
    virtual BOOL GetMargins (PAPER_SIZE ps, float *fMargins);

private:
	virtual void AdjustModeSettings (BOOL bDoFullBleed, MEDIATYPE ReqMedia,
									 MediaType *medium, Quality *quality);

}; //DJGenericVIP

class VIPFastDraftMode : public PrintMode
{
public:
    VIPFastDraftMode ();
}; // VIPFastDraftMode

class VIPGrayFastDraftMode : public GrayMode
{
public:
    VIPGrayFastDraftMode ();
}; // VIPGrayFastDraftMode

class VIPFastPhotoMode : public PrintMode
{
public:
    VIPFastPhotoMode ();
}; // VIPFastPhotoMode

class VIPAutoPQMode : public PrintMode
{
public:
    VIPAutoPQMode ();
}; // VIPAutoPQMode

#if defined(APDK_DJGENERICVIP) && defined (APDK_DJ9xxVIP)
//! DJGenericVIPProxy
/*!
******************************************************************************/
class DJGenericVIPProxy : public PrinterProxy
{
public:
    DJGenericVIPProxy() : PrinterProxy(
        "GenericVIP",                       // family name
        "deskjet 5100\0"
        "Deskjet 5400\0"
        "deskjet 5600\0"
		"Deskjet 5700\0"
		"deskjet 5800\0"
        "Deskjet 5900\0"
		"Deskjet 6500\0"
		"Deskjet 6600\0"
		"Deskjet 6800\0"
        "Deskjet 6940\0"
        "Deskjet 6980\0"
		"deskjet 9600\0"
		"Deskjet 9800\0"
        "Business Inkjet 1000\0"
		"hp business inkjet 1100\0"
   		"HP Business Inkjet 1200\0"
        "photosmart 7150\0"
        "photosmart 7350\0"
		"photosmart 7345\0"
        "photosmart 7550\0"
        "photosmart 7960\0"
        "photosmart 7760\0"
		"photosmart 7660\0"
        "photosmart 7260\0"
		"photosmart 7268\0"
		"Photosmart 7400\0"
        "Photosmart 7800\0"
        "Photosmart 8000\0"
		"Photosmart 8100\0"
		"Photosmart 8400\0"
		"Photosmart 8700\0"
		"Photosmart 8200\0"
		"Photosmart 320\0"
		"Photosmart 370\0"
		"Photosmart 380\0"
		"Photosmart 330\0"
        "Photosmart 420\0"
#ifdef APDK_MLC_PRINTER
		"PSC 1500\0"
		"PSC 1600\0"
        "PSC 2200\0"
        "psc 2300\0"
		"PSC 2350\0"
        "psc 2400\0"
        "psc 2500\0"
		"Officejet 7400\0"
		"Officejet 7300\0"
		"Officejet 7200\0"
		"Officejet 6200\0"
        "Officejet 6300\0"
        "Photosmart 2570\0"
		"Photosmart 2600\0"
		"Photosmart 2700\0"
        "Photosmart 3100\0"
        "Photosmart 3200\0"
        "Photosmart 3300\0"
#endif
    ) {m_iPrinterType = eDJGenericVIP;}
    inline Printer* CreatePrinter(SystemServices* pSS) const { return new DJGenericVIP(pSS); }
	inline PRINTER_TYPE GetPrinterType() const { return eDJGenericVIP;}
	inline unsigned int GetModelBit() const { return 0x80;}
};
#endif

APDK_END_NAMESPACE

#endif  // APDK_DJ_GENERIC_VIP_H
