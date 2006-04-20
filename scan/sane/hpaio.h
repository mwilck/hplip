/************************************************************************************\

  hpaio.h - HP SANE backend for multi-function peripherals (libsane-hpaio)

  (c) 2001-2004 Copyright Hewlett-Packard Development Company, LP

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

  Current Author: Don Welch
  Original Author: David Paschal 

\************************************************************************************/

#if !defined( __HPAIO_H__ )
#define __HPAIO_H__

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <sys/time.h>
#include <time.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <ctype.h>

#define BACKEND_NAME    hpaio
#define BACKEND_NAME_STR "hpaio"
#define SANE_DEBUG_BACKENDNAME hpaio

#include "sane.h"
#include "saneopts.h"
//#include "sanei_debug.h"
//#include "sanei_backend.h"
#include "io.h"
#include "mfpdtf.h"
#include "scl.h"
#include "tables.h"
#include "hpip.h"
#include "hplip_api.h"

typedef struct hpaioScanner_s HPAIO_RECORD;
#include "pml.h"

/************************************************************************************/

#define LEN_BUFFER    17408         /* 16384 + 1024, clj28xx used 16396 */
#define LEN_DEVICE_ID_STRING  4096
#define LEN_STRING_OPTION_VALUE 20
#define LEN_MODEL_RESPONSE  20

#define INFINITE_TIMEOUT                ((struct timeval *)0)
#define SCL_SEND_COMMAND_START_TIMEOUT          0
#define SCL_SEND_COMMAND_CONTINUE_TIMEOUT       2
#define SCL_INQUIRE_START_TIMEOUT           30
#define SCL_INQUIRE_CONTINUE_TIMEOUT            5
#define SCL_DEVICE_LOCK_TIMEOUT             0
#define SCL_PREPARE_SCAN_DEVICE_LOCK_MAX_RETRIES    4
#define SCL_PREPARE_SCAN_DEVICE_LOCK_DELAY      1
#define PML_SELECT_POLL_TIMEOUT             1
#define PML_UPLOAD_TIMEOUT              45
#define PML_START_SCAN_WAIT_ACTIVE_MAX_RETRIES      40
#define PML_START_SCAN_WAIT_ACTIVE_DELAY        1
#define MFPDTF_EARLY_READ_TIMEOUT           60
#define MFPDTF_LATER_READ_TIMEOUT           20
#define NON_MFPDTF_READ_START_TIMEOUT           60
#define NON_MFPDTF_READ_CONTINUE_TIMEOUT        2

#define PAD_VALUE_LINEART            0
#define PAD_VALUE_GRAYSCALE_COLOR    -1

enum hpaioOption_e { 
    
    OPTION_FIRST = 0,
    OPTION_NUM_OPTIONS = 0,
    
    GROUP_SCAN_MODE,
                    OPTION_SCAN_MODE,
                    OPTION_SCAN_RESOLUTION,
    GROUP_ADVANCED,
                    OPTION_CONTRAST,
                    OPTION_COMPRESSION,
                    OPTION_JPEG_COMPRESSION_FACTOR,
                    OPTION_BATCH_SCAN,
                    OPTION_ADF_MODE, 
                    OPTION_DUPLEX,

    GROUP_GEOMETRY,
                    OPTION_LENGTH_MEASUREMENT,
                    OPTION_TL_X,
                    OPTION_TL_Y,
                    OPTION_BR_X,
                    OPTION_BR_Y,

    OPTION_LAST };

#define STR_SCAN_MODE_LINEART "Lineart"
#define STR_SCAN_MODE_GRAYSCALE "Grayscale"
#define STR_SCAN_MODE_COLOR "Color"

enum hpaioScanMode_e { SCAN_MODE_FIRST = 0,
                       SCAN_MODE_LINEART = 0,
                       SCAN_MODE_GRAYSCALE,
                       SCAN_MODE_COLOR,
                       SCAN_MODE_LAST 
                     };

#define COMPRESSION_NONE  0x01
#define COMPRESSION_MH    0x02
#define COMPRESSION_MR    0x04
#define COMPRESSION_MMR   0x08
#define COMPRESSION_JPEG  0x10

#define STR_COMPRESSION_NONE  "None"
#define STR_COMPRESSION_MH  "MH"
#define STR_COMPRESSION_MR  "MR"
#define STR_COMPRESSION_MMR "MMR"
#define STR_COMPRESSION_JPEG  "JPEG"

#define MIN_JPEG_COMPRESSION_FACTOR 0
#define MAX_JPEG_COMPRESSION_FACTOR 100
/* To prevent "2252" asserts on OfficeJet 600 series: */
#define SAFER_JPEG_COMPRESSION_FACTOR 10

#define ADF_MODE_AUTO   0x01
#define ADF_MODE_FLATBED  0x02
#define ADF_MODE_ADF    0x04

#define STR_ADF_MODE_AUTO "Auto"
#define STR_ADF_MODE_FLATBED  "Flatbed"
#define STR_ADF_MODE_ADF  "ADF"

#define LENGTH_MEASUREMENT_UNKNOWN    0
#define LENGTH_MEASUREMENT_UNLIMITED    1
#define LENGTH_MEASUREMENT_APPROXIMATE    2
#define LENGTH_MEASUREMENT_PADDED   3
#define LENGTH_MEASUREMENT_EXACT    4

#define STR_LENGTH_MEASUREMENT_UNKNOWN    "Unknown"
#define STR_LENGTH_MEASUREMENT_UNLIMITED  "Unlimited"
#define STR_LENGTH_MEASUREMENT_APPROXIMATE  "Approximate"
#define STR_LENGTH_MEASUREMENT_PADDED   "Padded"
#define STR_LENGTH_MEASUREMENT_EXACT    "Exact"

#define STR_UNKNOWN   "???"

#define GEOMETRY_OPTION_TYPE    SANE_TYPE_FIXED
#define MILLIMETER_SHIFT_FACTOR   SANE_FIXED_SCALE_SHIFT

#define DECIPOINTS_PER_INCH     720
#define DEVPIXELS_PER_INCH      300
#define MILLIMETERS_PER_10_INCHES   254
#define INCHES_PER_254_MILLIMETERS  10

#define BYTES_PER_LINE(pixelsPerLine,bitsPerPixel) \
    ((((pixelsPerLine)*(bitsPerPixel))+7)/8)

#define INCHES_TO_MILLIMETERS(inches) \
    DivideAndShift(__LINE__, \
    (inches), \
    MILLIMETERS_PER_10_INCHES, \
    INCHES_PER_254_MILLIMETERS, \
    MILLIMETER_SHIFT_FACTOR)

#define DECIPIXELS_TO_MILLIMETERS(decipixels) \
    DivideAndShift(__LINE__, \
    (decipixels), \
    MILLIMETERS_PER_10_INCHES, \
    INCHES_PER_254_MILLIMETERS*hpaio->decipixelsPerInch, \
    MILLIMETER_SHIFT_FACTOR)

#define MILLIMETERS_TO_DECIPIXELS(millimeters) \
    DivideAndShift(__LINE__, \
    (millimeters), \
    INCHES_PER_254_MILLIMETERS*hpaio->decipixelsPerInch, \
    MILLIMETERS_PER_10_INCHES, \
    -MILLIMETER_SHIFT_FACTOR)

#define PIXELS_TO_MILLIMETERS(pixels,pixelsPerInch) \
    DivideAndShift(__LINE__, \
    (pixels), \
    MILLIMETERS_PER_10_INCHES, \
    (pixelsPerInch)*INCHES_PER_254_MILLIMETERS, \
    MILLIMETER_SHIFT_FACTOR)

#define MILLIMETERS_TO_PIXELS(millimeters,pixelsPerInch) \
    DivideAndShift(__LINE__, \
    (millimeters), \
    INCHES_PER_254_MILLIMETERS*(pixelsPerInch), \
    MILLIMETERS_PER_10_INCHES, \
    -MILLIMETER_SHIFT_FACTOR)

struct  hpaioScanner_s
{
        char deviceuri[128];
        int deviceid;
        int scan_channelid;
        int cmd_channelid;
        
        struct hpaioScanner_s * prev;
        struct hpaioScanner_s * next;

        SANE_Device     saneDevice; /* "vendor", "model" dynamically allocated. */
        SANE_Parameters prescanParameters;
        SANE_Parameters scanParameters;
        
        struct PmlObject_s *    firstPmlObject;
        struct PmlObject_s *    lastPmlObject;

        enum { SCANNER_TYPE_SCL, SCANNER_TYPE_PML } scannerType;
        int                     decipixelsPerInch;

        /* These are bitfields of COMPRESSION_* values. */
        int                     supportsScanMode[SCAN_MODE_LAST];
        SANE_String_Const       scanModeList[MAX_LIST_SIZE];
        enum hpaioScanMode_e    currentScanMode, effectiveScanMode;

        SANE_Range              resolutionRange;
        SANE_Int                resolutionList[MAX_LIST_SIZE];
        SANE_Int                lineartResolutionList[MAX_LIST_SIZE];  /* 300 dpi. */
        SANE_Int                currentResolution, effectiveResolution;

        SANE_Range              contrastRange;
        SANE_Int                defaultContrast, currentContrast;

        SANE_String_Const       compressionList[MAX_LIST_SIZE];
        int                     defaultCompression[SCAN_MODE_LAST];
        SANE_Int                currentCompression;  /* One of the COMPRESSION_* values. */

        SANE_Range              jpegCompressionFactorRange;
        SANE_Int                defaultJpegCompressionFactor;
        SANE_Int                currentJpegCompressionFactor;

        SANE_Bool               currentBatchScan;
        int                     beforeScan;
        int                     alreadyPreAdvancedDocument;
        int                     alreadyPostAdvancedDocument;
        int                     noDocsConditionPending;

        int                     supportedAdfModes;
        SANE_String_Const       adfModeList[MAX_LIST_SIZE];
        int                     currentAdfMode;
        int                     currentPageNumber;

        int                     supportsDuplex;
        SANE_Bool               currentDuplex;
        int                     currentSideNumber;

        SANE_Int                currentLengthMeasurement;
        SANE_String_Const       lengthMeasurementList[MAX_LIST_SIZE];

        SANE_Range              tlxRange, tlyRange, brxRange, bryRange;
        SANE_Fixed              currentTlx, currentTly, currentBrx, currentBry;
        SANE_Fixed              effectiveTlx,
                                effectiveTly,
                                effectiveBrx,
                                effectiveBry;

        SANE_Option_Descriptor  option[OPTION_LAST];

        Mfpdtf_t                mfpdtf;
        IP_HANDLE               hJob;
        int                     fromDenali;
        int                     preDenali;
        int                     denali;
        unsigned char           inBuffer[LEN_BUFFER];     /* mfpdtf block buffer */
        int                     bufferOffset;
        int                     bufferBytesRemaining;
        int                     totalBytesRemaining;
        int                     endOfData;
        int BlockSize;                                    /* mfpdtf block size, including fixed header */
        int BlockIndex;                                   /* record index in mfpdtf block */
        int RecordSize;                                    /* record size, does not include header */
        int RecordIndex;                                   /* data index in record */
        int mfpdtf_done; 
        int mfpdtf_timeout_cnt; 
        int pml_timeout_cnt;                              /* pml done timeout count */ 
        int pml_done;
        int ip_done;
        int page_done;
        int upload_state;                                 /* last pml upload state */

        struct 
        {
                char            compat1150[LEN_MODEL_RESPONSE + 1];
                char            compatPost1150[LEN_MODEL_RESPONSE + 1];
                int             compat;
                char            decipixelChar;

                int             minXRes, minYRes;
                int             maxXRes, maxYRes;
                int             maxXExtent, maxYExtent;

                int             adfCapability;
                int             unloadAfterScan;

                PmlObject_t     objSupportedFunctions;
        } scl;

        struct 
        {
                PmlObject_t     objScannerStatus,
                                objResolutionRange,
                                objUploadTimeout,
                                objContrast,
                                objResolution,
                                objPixelDataType,
                                objCompression,
                                objCompressionFactor,
                                objUploadError,
                                objUploadState,
                                objAbcThresholds,
                                objSharpeningCoefficient,
                                objNeutralClipThresholds,
                                objToneMap,
                                objCopierReduction,
                                objScanToken,
                                objModularHardware;

                char            scanToken[ PML_MAX_VALUE_LEN ];
                char            zeroScanToken[ PML_MAX_VALUE_LEN ];
                int             lenScanToken;
                int             scanTokenIsSet;

                int             openFirst;
                int             dontResetBeforeNextNonBatchPage;
                int             startNextBatchPageEarly;
                int             flatbedCapability;

                int             alreadyRestarted;
                int             scanDone;
                int             previousUploadState;
        } pml;
};

typedef struct hpaioScanner_s * hpaioScanner_t;

#define UNDEFINED_MODEL(hpaio) (!hpaio->saneDevice.model)

#define _SET_DEFAULT_MODEL(hpaio,s,len) \
  do { \
    if (UNDEFINED_MODEL(hpaio)) { \
      hpaio->saneDevice.model=malloc(len+1); \
      memcpy((char *)hpaio->saneDevice.model,s,len); \
      ((char *)hpaio->saneDevice.model)[len]=0; \
    } \
  } while(0)
#define SET_DEFAULT_MODEL(hpaio,s) _SET_DEFAULT_MODEL(hpaio,s,strlen(s))

#define ADD_XFORM(x) \
  do { \
    pXform->eXform=x; \
    DBG( 0, "hpaio:%s: sane_hpaio_start: added xform=%d.\n", \
      hpaio->saneDevice.name,pXform->eXform); \
    pXform++; \
  } while(0)

#define FIX_GEOMETRY(low,high,min,max) \
  do { \
    if (high<low) high=low; \
    if (high==low) { \
      if (high==max) { \
        low--; \
      } else { \
        high++; \
      } \
    } \
  } while(0)

SANE_Status hpaioScannerToSaneStatus( hpaioScanner_t hpaio );
SANE_Status hpaioScannerToSaneError( hpaioScanner_t hpaio );

#endif
