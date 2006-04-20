/************************************************************************************\

  hpaio.c - HP SANE backend for multi-function peripherals (libsane-hpaio)

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

#include "hpaio.h"

static SANE_Device ** hpaioDeviceList = 0;

static hpaioScanner_t FirstScanner = 0;
static hpaioScanner_t LastScanner = 0;

static void hpaioAddScanner( hpaioScanner_t scanner ) 
{
    if( !FirstScanner )
    {
        FirstScanner = scanner;
    }
    scanner->prev = LastScanner;
    scanner->next = 0;
    if( LastScanner )
    {
        LastScanner->next = scanner;
    }
    LastScanner = scanner;
}

static hpaioScanner_t hpaioFindScanner( SANE_String_Const name )
{
    hpaioScanner_t p = FirstScanner;
    
    while( p != LastScanner )
    {
        if( strcasecmp( name, p->saneDevice.name ) == 0 )
            return p;
        
        p++;
    }
    
    return NULL;
}

SANE_Status hpaioScannerToSaneError( hpaioScanner_t hpaio )
{
    SANE_Status retcode;

    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    {
        int sclError;

        retcode = SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                              SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                              SCL_INQ_CURRENT_ERROR,
                              &sclError,
                              0,
                              0 );

        if( retcode == SANE_STATUS_UNSUPPORTED )
        {
            retcode = SANE_STATUS_GOOD;
        }
        else if( retcode == SANE_STATUS_GOOD )
        {
            DBG( 0,  "hpaio: hpaioScannerToSaneError: "
                            "sclError=%d.\n",
                            sclError );

            switch( sclError )
            {
                case SCL_ERROR_UNRECOGNIZED_COMMAND:
                case SCL_ERROR_PARAMETER_ERROR:
                    retcode = SANE_STATUS_UNSUPPORTED;
                    break;

                case SCL_ERROR_NO_MEMORY:
                    retcode = SANE_STATUS_NO_MEM;
                    break;

                case SCL_ERROR_CANCELLED:
                    retcode = SANE_STATUS_CANCELLED;
                    break;

                case SCL_ERROR_PEN_DOOR_OPEN:
                    retcode = SANE_STATUS_COVER_OPEN;
                    break;

                case SCL_ERROR_SCANNER_HEAD_LOCKED:
                case SCL_ERROR_ADF_PAPER_JAM:
                case SCL_ERROR_HOME_POSITION_MISSING:
                case SCL_ERROR_ORIGINAL_ON_GLASS:
                    retcode = SANE_STATUS_JAMMED;
                    break;

                case SCL_ERROR_PAPER_NOT_LOADED:
                    retcode = SANE_STATUS_NO_DOCS;
                    break;

                default:
                    retcode = SANE_STATUS_IO_ERROR;
                    break;
            }
        }
    }
    else /* if (hpaio->scannerType==SCANNER_TYPE_PML) */
    {
        int pmlError, type;

        //if( ptalPmlRequestGet( hpaio->pml.objUploadError, 0 ) == ERROR )
        if( PmlRequestGet( hpaio->deviceid, hpaio->cmd_channelid, hpaio->pml.objUploadError ) == ERROR )
        {
            retcode = SANE_STATUS_GOOD;
        }
        else if( PmlGetIntegerValue( hpaio->pml.objUploadError,
                                         &type,
                                         &pmlError ) == ERROR )
        {
            DBG( 0,  "hpaio: hpaioScannerToSaneError: "
                           "PmlGetIntegerValue failed, type=%d!\n",
                           type );
            retcode = SANE_STATUS_IO_ERROR;
        }
        else
        {
            DBG( 0,  "hpaio: hpaioScannerToSaneError: "
                            "pmlError=%d.\n",
                            pmlError );

            switch( pmlError )
            {
                case PML_UPLOAD_ERROR_SCANNER_JAM:
                    retcode = SANE_STATUS_JAMMED;
                    break;

                case PML_UPLOAD_ERROR_MLC_CHANNEL_CLOSED:
                case PML_UPLOAD_ERROR_STOPPED_BY_HOST:
                case PML_UPLOAD_ERROR_STOP_KEY_PRESSED:
                    retcode = SANE_STATUS_CANCELLED;
                    break;

                case PML_UPLOAD_ERROR_NO_DOC_IN_ADF:
                case PML_UPLOAD_ERROR_DOC_LOADED:
                    retcode = SANE_STATUS_NO_DOCS;
                    break;

                case PML_UPLOAD_ERROR_COVER_OPEN:
                    retcode = SANE_STATUS_COVER_OPEN;
                    break;

                case PML_UPLOAD_ERROR_DEVICE_BUSY:
                    retcode = SANE_STATUS_DEVICE_BUSY;
                    break;

                default:
                    retcode = SANE_STATUS_IO_ERROR;
                    break;
            }
        }
    }

    DBG( 0,  "hpaio: hpaioScannerToSaneError returns %d.\n",
                    retcode );
    return retcode;
}


SANE_Status hpaioScannerToSaneStatus( hpaioScanner_t hpaio )
{
//BREAKPOINT;
    
    SANE_Status retcode;

    //    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    //    {
        int sclStatus;

        retcode = SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                              SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                              SCL_INQ_ADF_FEED_STATUS,
                              &sclStatus,
                              0,
                              0 );

        if( retcode == SANE_STATUS_UNSUPPORTED )
        {
            retcode = SANE_STATUS_GOOD;
        }
        else if( retcode == SANE_STATUS_GOOD )
        {
            DBG( 0,  "hpaio: hpaioScannerToSaneStatus: "
                            "sclStatus=%d.\n",
                            sclStatus );

            switch( sclStatus )
            {
                case SCL_ADF_FEED_STATUS_OK:
                    retcode = SANE_STATUS_GOOD;
                    break;

                case SCL_ADF_FEED_STATUS_BUSY:
                    /* retcode=SANE_STATUS_DEVICE_BUSY; */
                    retcode = SANE_STATUS_GOOD;
                    break;

                case SCL_ADF_FEED_STATUS_PAPER_JAM:
                case SCL_ADF_FEED_STATUS_ORIGINAL_ON_GLASS:
                    retcode = SANE_STATUS_JAMMED;
                    break;

                case SCL_ADF_FEED_STATUS_PORTRAIT_FEED:
                    retcode = SANE_STATUS_UNSUPPORTED;
                    break;

                default:
                    retcode = SANE_STATUS_IO_ERROR;
                    break;
            }
        }

    DBG( 0,  "hpaio: hpaioScannerToSaneStatus returns %d.\n",
                    retcode );
    return retcode;
}

static int hpaioScannerIsUninterruptible( hpaioScanner_t hpaio,
                                          int * pUploadState )
{
    int uploadState;
    if( !pUploadState )
    {
        pUploadState = &uploadState;
    }

    return ( hpaio->scannerType == SCANNER_TYPE_PML &&
             hpaio->pml.scanDone &&
             PmlRequestGet( hpaio->deviceid, hpaio->cmd_channelid, 
                            hpaio->pml.objUploadState ) != ERROR &&
             PmlGetIntegerValue( hpaio->pml.objUploadState, 0, pUploadState ) != ERROR &&
             ( *pUploadState == PML_UPLOAD_STATE_START ||
               *pUploadState == PML_UPLOAD_STATE_ACTIVE ||
               *pUploadState == PML_UPLOAD_STATE_NEWPAGE ) );
}

static SANE_Status hpaioResetScanner( hpaioScanner_t hpaio )
{
//BREAKPOINT;
    
    SANE_Status retcode;

    DBG( 0,  "\nhpaio: hpaioResetScanner()\n" ); 

    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    {
        retcode = SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_RESET, 0 );
        if( retcode != SANE_STATUS_GOOD )
        {
            return retcode;
        }
    }
    else /* if (hpaio->scannerType==SCANNER_TYPE_PML) */
    {
        if( !hpaioScannerIsUninterruptible( hpaio, 0 ) )
        {
            PmlSetIntegerValue( hpaio->pml.objUploadState,
                                PML_TYPE_ENUMERATION,
                                PML_UPLOAD_STATE_IDLE );
                                
            if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                    hpaio->pml.objUploadState, 0, 0 ) == ERROR )
            {
                return SANE_STATUS_IO_ERROR;
            }
        }

        /* Clear upload error for the sake of the LaserJet 1100A. */
        PmlSetIntegerValue( hpaio->pml.objUploadError,
                            PML_TYPE_SIGNED_INTEGER,
                            0 );
                            
        PmlRequestSet( hpaio->deviceid, hpaio->cmd_channelid, hpaio->pml.objUploadError );  /* No retry. */
    }

    return SANE_STATUS_GOOD;
}

static PmlObject_t hpaioPmlAllocate( hpaioScanner_t hpaio )
{
    int size = sizeof( struct PmlObject_s );
    PmlObject_t obj;

    /* Malloc and zero object. */
    obj = malloc( size );

    memset( obj, 0, size );

    /* Insert into linked list of PML objects for this device. */
    if( !hpaio->firstPmlObject )
    {
        hpaio->firstPmlObject = obj;
    }
    obj->prev = hpaio->lastPmlObject;
    obj->next = 0;
    if( hpaio->lastPmlObject )
    {
        hpaio->lastPmlObject->next = obj;
    }
    hpaio->lastPmlObject = obj;

    return obj;
}

static PmlObject_t hpaioPmlAllocateID( hpaioScanner_t hpaio, char * oid )
{
    PmlObject_t obj = hpaioPmlAllocate( hpaio );

    if( !obj )
    {
        DBG( 0, "hpaioPmlAllocateID: out of memory!\n" );
    }

    PmlSetID( obj, oid );

    return obj;
}

static void hpaioPmlDeallocateObjects( hpaioScanner_t hpaio )
{
    //int count = 0;
    PmlObject_t current, next;

    current = hpaio->firstPmlObject;
    
    while( current )
    {
        next = current->next;
        
        free( current );

        current = next;
    }
}

static SANE_Status hpaioPmlAllocateObjects( hpaioScanner_t hpaio )
{
    DBG( 0,  "hpaio: hpaioPmlAllocateObjects()\n" ); 
    
    if( hpaio->scannerType == SCANNER_TYPE_PML && !hpaio->pml.objScanToken )
    {
        int len;

        /* SNMP oids for PML. */
        hpaio->pml.objScannerStatus = hpaioPmlAllocateID( hpaio,          "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.2.1.0" );
        hpaio->pml.objResolutionRange = hpaioPmlAllocateID( hpaio,        "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.2.3.0" );
        hpaio->pml.objUploadTimeout = hpaioPmlAllocateID( hpaio,          "1.3.6.1.4.1.11.2.3.9.4.2.1.1.1.18.0" );
        hpaio->pml.objContrast = hpaioPmlAllocateID( hpaio,               "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.1.0" );
        hpaio->pml.objResolution = hpaioPmlAllocateID( hpaio,             "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.2.0" );
        hpaio->pml.objPixelDataType = hpaioPmlAllocateID( hpaio,          "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.3.0" );
        hpaio->pml.objCompression = hpaioPmlAllocateID( hpaio,            "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.4.0" );
        hpaio->pml.objCompressionFactor = hpaioPmlAllocateID( hpaio,      "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.5.0" );
        hpaio->pml.objUploadError = hpaioPmlAllocateID( hpaio,            "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.6.0" );
        hpaio->pml.objUploadState = hpaioPmlAllocateID( hpaio,            "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.12.0" );
        hpaio->pml.objAbcThresholds = hpaioPmlAllocateID( hpaio,          "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.14.0" );
        hpaio->pml.objSharpeningCoefficient = hpaioPmlAllocateID( hpaio,  "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.15.0" );
        hpaio->pml.objNeutralClipThresholds = hpaioPmlAllocateID( hpaio,  "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.31.0" );
        hpaio->pml.objToneMap = hpaioPmlAllocateID( hpaio,                "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.32.0" );
        hpaio->pml.objCopierReduction = hpaioPmlAllocateID( hpaio,        "1.3.6.1.4.1.11.2.3.9.4.2.1.5.1.4.0" );
        hpaio->pml.objScanToken = hpaioPmlAllocateID( hpaio,              "1.3.6.1.4.1.11.2.3.9.4.2.1.1.1.25.0" );
        hpaio->pml.objModularHardware = hpaioPmlAllocateID( hpaio,        "1.3.6.1.4.1.11.2.3.9.4.2.1.2.2.1.75.0" );

//BREAKPOINT;

        if( PmlRequestGet( hpaio->deviceid, hpaio->cmd_channelid, 
                           hpaio->pml.objScanToken ) != ERROR &&
            
            ( len = PmlGetValue( hpaio->pml.objScanToken,
                                 0,
                                 hpaio->pml.scanToken,
                                 PML_MAX_VALUE_LEN ) ) > 0 )
        {
            int i;
            hpaio->pml.lenScanToken = len;
            DBG( 0,  "hpaio: lenScanToken=%d.\n",
                            hpaio->pml.lenScanToken );
            for( i = 0; i < len; i++ )
            {
                hpaio->pml.scanToken[i] = 0;
                hpaio->pml.zeroScanToken[i] = 0;
            }
            gettimeofday( ( struct timeval * ) hpaio->pml.scanToken, 0 );
            i = sizeof( struct timeval );
            *( ( pid_t * ) ( hpaio->pml.scanToken + i ) ) = getpid();
            i += sizeof( pid_t );
            *( ( pid_t * ) ( hpaio->pml.scanToken + i ) ) = getppid();

#if 0
            if( getenv( "SANE_HPAIO_RESET_SCAN_TOKEN" ) )
            {
                PmlSetValue( hpaio->pml.objScanToken,
                             PML_TYPE_BINARY,
                             hpaio->pml.zeroScanToken,
                             hpaio->pml.lenScanToken );
                             
                PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                    hpaio->pml.objScanToken, 0, 0 );
            }
#endif
        }
    }

    return SANE_STATUS_GOOD;
}

static int hpaioConnClose( hpaioScanner_t hpaio )
{
    DBG( 0,  "\nhpaio: hpaioConnClose()\n" ); 

    if( hpaio->pml.scanTokenIsSet )
    {
        PmlSetValue( hpaio->pml.objScanToken,
                     PML_TYPE_BINARY,
                     hpaio->pml.zeroScanToken,
                     hpaio->pml.lenScanToken );
                     
        PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, hpaio->pml.objScanToken, 0, 0 );
        hpaio->pml.scanTokenIsSet = 0;
    }

    if (hpaio->cmd_channelid > 0)
       hplip_CloseChannel( hpaio->deviceid, hpaio->cmd_channelid );
    hpaio->cmd_channelid = -1;
    if (hpaio->scan_channelid > 0)
       hplip_CloseChannel( hpaio->deviceid, hpaio->scan_channelid );
    hpaio->scan_channelid = -1;

    return 0;
} // hpaioConnClose()

static SANE_Status hpaioConnOpen( hpaioScanner_t hpaio )
{
    SANE_Status retcode;

    DBG( 0, "\nhpaio: hpaioConnOpen()\n" );
    DBG( 0, "hpaio: openFirst=%d\n", hpaio->pml.openFirst );
    
    if (hpaio->scannerType==SCANNER_TYPE_SCL) 
    {
       hpaio->scan_channelid = hplip_OpenChannel(hpaio->deviceid, "HP-SCAN");
       if(hpaio->scan_channelid < 0)
       {
          retcode = SANE_STATUS_DEVICE_BUSY;
          goto abort;
       }
    }

    hpaio->cmd_channelid = hplip_OpenChannel(hpaio->deviceid, "HP-MESSAGE");
    if(hpaio->cmd_channelid < 0)
    {
       retcode = SANE_STATUS_IO_ERROR;
       goto abort;
    }

    if (hpaio->scannerType==SCANNER_TYPE_PML)
    {
        hpaioPmlAllocateObjects( hpaio ); // sets up scan token

        if( !hpaio->pml.openFirst )
        {
            DBG( 0, "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" );
        }
        else if( hpaio->pml.lenScanToken )
        {
            PmlSetValue( hpaio->pml.objScanToken,
                         PML_TYPE_BINARY,
                         hpaio->pml.scanToken,
                         hpaio->pml.lenScanToken );
            
            if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                    hpaio->pml.objScanToken, 0, 0 ) == ERROR )
            {
                retcode = SANE_STATUS_DEVICE_BUSY;
                goto abort;
            }
            hpaio->pml.scanTokenIsSet = 1;
        }
    }

    retcode = hpaioResetScanner( hpaio );
    
    DBG( 0, "retcode=%d\n", retcode );
    
abort:
    if( retcode != SANE_STATUS_GOOD )
    {
        SendScanEvent( hpaio->deviceuri, 2002, "error" );
    }
    return retcode;
}

static SANE_Status hpaioConnPrepareScan( hpaioScanner_t hpaio )
{
    SANE_Status retcode;
    int i;

    DBG( 0,  "\nhpaio: hpaioConnPrepareScan()\n" );

    /* ADF may already have channel(s) open. */
    if (hpaio->cmd_channelid < 0)
    {
       retcode = hpaioConnOpen( hpaio );
    
       if( retcode != SANE_STATUS_GOOD )
       {
          return retcode;
       }
    }

    //    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    //    {

        /* Reserve scanner and make sure it got reserved. */
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_SET_DEVICE_LOCK, 1 );
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_DEVICE_LOCK_TIMEOUT,
                        SCL_DEVICE_LOCK_TIMEOUT );
                        
        for( i = 0; ; i++ )
        {
            char buffer[LEN_SCL_BUFFER];
            int len, j;
            struct timeval tv1, tv2;
            gettimeofday( &tv1, 0 );
            
            if( SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                            SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                            SCL_INQ_SESSION_ID,
                            &len,
                            buffer,
                            LEN_SCL_BUFFER ) != SANE_STATUS_GOOD )
            {
                break;
            }
            
            gettimeofday( &tv2, 0 );
            
            for( j = 0; j < len && buffer[j] == '0'; j++ ) ;
            
            if( j < len )
            {
                break;
            }
            
            if( i >= SCL_PREPARE_SCAN_DEVICE_LOCK_MAX_RETRIES )
            {
                return SANE_STATUS_DEVICE_BUSY;
            }
            
            DBG( 0, "hpaio: hpaioConnPrepareScan: "
                    "Waiting for device lock.\n" );
                     
            if( ( ( unsigned ) ( tv2.tv_sec - tv1.tv_sec ) ) <= SCL_PREPARE_SCAN_DEVICE_LOCK_DELAY )
            {
                sleep( SCL_PREPARE_SCAN_DEVICE_LOCK_DELAY );
            }
        }

    SendScanEvent( hpaio->deviceuri, 2000, "event" );
 
    return SANE_STATUS_GOOD;
}

static void hpaioConnEndScan( hpaioScanner_t hpaio )
{
    DBG( 0,  "\nhpaio: hpaioConnEndScan()\n" ); 

    hpaioResetScanner( hpaio );
    hpaioConnClose( hpaio );
    
    SendScanEvent( hpaio->deviceuri, 2001, "event" );
}

static SANE_Status hpaioSetDefaultValue( hpaioScanner_t hpaio, int option )
{
    DBG( 0,  "\nhpaio: hpaioSetDefaultValue(option=%d)\n",
             option );

    switch( option )
    {
        case OPTION_SCAN_MODE:
            if( hpaio->supportsScanMode[SCAN_MODE_COLOR] )
            {
                hpaio->currentScanMode = SCAN_MODE_COLOR;
            }
            else if( hpaio->supportsScanMode[SCAN_MODE_GRAYSCALE] )
            {
                hpaio->currentScanMode = SCAN_MODE_GRAYSCALE;
            }
            else /* if (hpaio->supportsScanMode[SCAN_MODE_LINEART]) */
            {
                hpaio->currentScanMode = SCAN_MODE_LINEART;
            }
            break;

        case OPTION_SCAN_RESOLUTION:
            if( hpaio->option[OPTION_SCAN_RESOLUTION].constraint_type == SANE_CONSTRAINT_WORD_LIST )
            {
                hpaio->currentResolution = NumListGetFirst( ( SANE_Int * )
                    hpaio->option[OPTION_SCAN_RESOLUTION].constraint.word_list );
            }
            else
            {
                hpaio->currentResolution = hpaio->resolutionRange.min;
            }
            break;

        case OPTION_CONTRAST:
            hpaio->currentContrast = hpaio->defaultContrast;
            break;

        case OPTION_COMPRESSION:
            {
//BREAKPOINT;
                int supportedCompression = hpaio->supportsScanMode[hpaio->currentScanMode];
                int defaultCompression = hpaio->defaultCompression[hpaio->currentScanMode];

                if( supportedCompression & defaultCompression )
                {
                    hpaio->currentCompression = defaultCompression;
                }
                else if( supportedCompression & COMPRESSION_JPEG )
                {
                    hpaio->currentCompression = COMPRESSION_JPEG;
                }
                else if( supportedCompression & COMPRESSION_MH )
                {
                    hpaio->currentCompression = COMPRESSION_MH;
                }
                else if( supportedCompression & COMPRESSION_MR )
                {
                    hpaio->currentCompression = COMPRESSION_MR;
                }
                else if( supportedCompression & COMPRESSION_MMR )
                {
                    hpaio->currentCompression = COMPRESSION_MMR;
                }
                else
                {
                    hpaio->currentCompression = COMPRESSION_NONE;
                }
            }
            break;

        case OPTION_JPEG_COMPRESSION_FACTOR:
            hpaio->currentJpegCompressionFactor = hpaio->defaultJpegCompressionFactor;
            break;

        case OPTION_BATCH_SCAN:
            hpaio->currentBatchScan = SANE_FALSE;
            break;

        case OPTION_ADF_MODE:
            if( hpaio->supportedAdfModes & ADF_MODE_AUTO )
            {
                if( hpaio->scannerType == SCANNER_TYPE_PML &&
                    !hpaio->pml.flatbedCapability &&
                    hpaio->supportedAdfModes & ADF_MODE_ADF )
                {
                    goto defaultToAdf;
                }
                hpaio->currentAdfMode = ADF_MODE_AUTO;
            }
            else if( hpaio->supportedAdfModes & ADF_MODE_FLATBED )
            {
                hpaio->currentAdfMode = ADF_MODE_FLATBED;
            }
            else if( hpaio->supportedAdfModes & ADF_MODE_ADF )
            {
                defaultToAdf:
                hpaio->currentAdfMode = ADF_MODE_ADF;
            }
            else
            {
                hpaio->currentAdfMode = ADF_MODE_AUTO;
            }
            break;

        case OPTION_DUPLEX:
            hpaio->currentDuplex = SANE_FALSE;
            break;

        case OPTION_LENGTH_MEASUREMENT:
            hpaio->currentLengthMeasurement = LENGTH_MEASUREMENT_PADDED;
            break;

        case OPTION_TL_X:
            hpaio->currentTlx = hpaio->tlxRange.min;
            break;

        case OPTION_TL_Y:
            hpaio->currentTly = hpaio->tlyRange.min;
            break;

        case OPTION_BR_X:
            hpaio->currentBrx = hpaio->brxRange.max;
            break;

        case OPTION_BR_Y:
            hpaio->currentBry = hpaio->bryRange.max;
            break;

        default:
            return SANE_STATUS_INVAL;
    }

    return SANE_STATUS_GOOD;
}

static int hpaioUpdateDescriptors( hpaioScanner_t hpaio, int option )
{
    int initValues = ( option == OPTION_FIRST );
    int reload = 0;

    DBG( 0,  "\nhpaio: hpaioUpdateDescriptors(option=%d)\n", option );

    /* OPTION_SCAN_MODE: */
    if( initValues )
    {
        StrListClear( hpaio->scanModeList );
        if( hpaio->supportsScanMode[SCAN_MODE_LINEART] )
        {
            StrListAdd( hpaio->scanModeList, STR_SCAN_MODE_LINEART );
        }
        if( hpaio->supportsScanMode[SCAN_MODE_GRAYSCALE] )
        {
            StrListAdd( hpaio->scanModeList, STR_SCAN_MODE_GRAYSCALE );
        }
        if( hpaio->supportsScanMode[SCAN_MODE_COLOR] )
        {
            StrListAdd( hpaio->scanModeList, STR_SCAN_MODE_COLOR );
        }
        hpaioSetDefaultValue( hpaio, OPTION_SCAN_MODE );
        reload |= SANE_INFO_RELOAD_OPTIONS;
        reload |= SANE_INFO_RELOAD_PARAMS;
    }
    else if( option == OPTION_SCAN_MODE )
    {
        reload |= SANE_INFO_RELOAD_PARAMS;
    }

    /* OPTION_SCAN_RESOLUTION: */
    if( hpaio->option[OPTION_SCAN_RESOLUTION].constraint_type ==
        SANE_CONSTRAINT_WORD_LIST )
    {
        SANE_Int ** pList = ( SANE_Int ** ) &hpaio->option[OPTION_SCAN_RESOLUTION].constraint.word_list;

        if( hpaio->currentScanMode == SCAN_MODE_LINEART )
        {
            if( *pList != hpaio->lineartResolutionList )
            {
                *pList = hpaio->lineartResolutionList;
                reload |= SANE_INFO_RELOAD_OPTIONS;
            }
        }
        else
        {
            if( *pList != hpaio->resolutionList )
            {
                *pList = hpaio->resolutionList;
                reload |= SANE_INFO_RELOAD_OPTIONS;
            }
        }
        if( initValues || !NumListIsInList( *pList,
                                             hpaio->currentResolution ) )
        {
            hpaioSetDefaultValue( hpaio, OPTION_SCAN_RESOLUTION );
            reload |= SANE_INFO_RELOAD_OPTIONS;
            reload |= SANE_INFO_RELOAD_PARAMS;
        }
    }
    else
    {
        if( initValues ||
            hpaio->currentResolution<hpaio->resolutionRange.min ||
            hpaio->currentResolution>hpaio->resolutionRange.max )
        {
            hpaioSetDefaultValue( hpaio, OPTION_SCAN_RESOLUTION );
            reload |= SANE_INFO_RELOAD_OPTIONS;
            reload |= SANE_INFO_RELOAD_PARAMS;
        }
    }
    if( option == OPTION_SCAN_RESOLUTION )
    {
        reload |= SANE_INFO_RELOAD_PARAMS;
    }

    /* OPTION_CONTRAST: */
    if( initValues )
    {
        hpaioSetDefaultValue( hpaio, OPTION_CONTRAST );
    }

    /* OPTION_COMPRESSION: */
    {
//BREAKPOINT;
        int supportedCompression = hpaio->supportsScanMode[hpaio->currentScanMode];
        if( initValues ||
            !( supportedCompression & hpaio->currentCompression ) ||
            ( ( ( supportedCompression & COMPRESSION_NONE ) != 0 ) !=
              ( StrListIsInList( hpaio->compressionList,
                                      STR_COMPRESSION_NONE ) != 0 ) ) ||
            ( ( ( supportedCompression & COMPRESSION_MH ) != 0 ) !=
              ( StrListIsInList( hpaio->compressionList,
                                      STR_COMPRESSION_MH ) != 0 ) ) ||
            ( ( ( supportedCompression & COMPRESSION_MR ) != 0 ) !=
              ( StrListIsInList( hpaio->compressionList,
                                      STR_COMPRESSION_MR ) != 0 ) ) ||
            ( ( ( supportedCompression & COMPRESSION_MMR ) != 0 ) !=
              ( StrListIsInList( hpaio->compressionList,
                                      STR_COMPRESSION_MMR ) != 0 ) ) ||
            ( ( ( supportedCompression & COMPRESSION_JPEG ) != 0 ) !=
              ( StrListIsInList( hpaio->compressionList,
                                      STR_COMPRESSION_JPEG ) != 0 ) ) )
        {
            StrListClear( hpaio->compressionList );
            if( supportedCompression & COMPRESSION_NONE )
            {
                StrListAdd( hpaio->compressionList, STR_COMPRESSION_NONE );
            }
            if( supportedCompression & COMPRESSION_MH )
            {
                StrListAdd( hpaio->compressionList, STR_COMPRESSION_MH );
            }
            if( supportedCompression & COMPRESSION_MR )
            {
                StrListAdd( hpaio->compressionList, STR_COMPRESSION_MR );
            }
            if( supportedCompression & COMPRESSION_MMR )
            {
                StrListAdd( hpaio->compressionList, STR_COMPRESSION_MMR );
            }
            if( supportedCompression & COMPRESSION_JPEG )
            {
                StrListAdd( hpaio->compressionList, STR_COMPRESSION_JPEG );
            }
            hpaioSetDefaultValue( hpaio, OPTION_COMPRESSION );
            reload |= SANE_INFO_RELOAD_OPTIONS;
        }
    }

    /* OPTION_JPEG_COMPRESSION_FACTOR: */
    if( initValues ||
        ( ( hpaio->currentCompression == COMPRESSION_JPEG ) !=
          ( ( hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].cap & SANE_CAP_INACTIVE ) == 0 ) ) )
    {
        if( hpaio->currentCompression == COMPRESSION_JPEG )
        {
            hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].cap &= ~SANE_CAP_INACTIVE;
        }
        else
        {
            hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].cap |= SANE_CAP_INACTIVE;
        }
        hpaioSetDefaultValue( hpaio, OPTION_JPEG_COMPRESSION_FACTOR );
        reload |= SANE_INFO_RELOAD_OPTIONS;
    }

    /* OPTION_BATCH_SCAN: */
    if( initValues )
    {
        hpaioSetDefaultValue( hpaio, OPTION_BATCH_SCAN );
        if( hpaio->preDenali )
        {
            hpaio->option[OPTION_BATCH_SCAN].cap |= SANE_CAP_INACTIVE;
        }
        reload |= SANE_INFO_RELOAD_OPTIONS;
    }
    if( !hpaio->currentBatchScan )
    {
        hpaio->noDocsConditionPending = 0;
    }

    /* OPTION_ADF_MODE: */
    if( initValues )
    {
        StrListClear( hpaio->adfModeList );
        if( hpaio->supportedAdfModes & ADF_MODE_AUTO )
        {
            StrListAdd( hpaio->adfModeList, STR_ADF_MODE_AUTO );
        }
        if( hpaio->supportedAdfModes & ADF_MODE_FLATBED )
        {
            StrListAdd( hpaio->adfModeList, STR_ADF_MODE_FLATBED );
        }
        if( hpaio->supportedAdfModes & ADF_MODE_ADF )
        {
            StrListAdd( hpaio->adfModeList, STR_ADF_MODE_ADF );
        }
        hpaioSetDefaultValue( hpaio, OPTION_ADF_MODE );
        reload |= SANE_INFO_RELOAD_OPTIONS;
    }

    /* OPTION_DUPLEX: */
    if( initValues ||
        ( ( hpaio->supportsDuplex &&
            hpaio->currentAdfMode != ADF_MODE_FLATBED ) !=
          ( ( hpaio->option[OPTION_DUPLEX].cap & SANE_CAP_INACTIVE ) == 0 ) ) )
    {
        if( hpaio->supportsDuplex &&
            hpaio->currentAdfMode != ADF_MODE_FLATBED )
        {
            hpaio->option[OPTION_DUPLEX].cap &= ~SANE_CAP_INACTIVE;
        }
        else
        {
            hpaio->option[OPTION_DUPLEX].cap |= SANE_CAP_INACTIVE;
        }
        hpaioSetDefaultValue( hpaio, OPTION_DUPLEX );
        reload |= SANE_INFO_RELOAD_OPTIONS;
    }

    /* OPTION_LENGTH_MEASUREMENT: */
    if( initValues )
    {
        hpaioSetDefaultValue( hpaio, OPTION_LENGTH_MEASUREMENT );
        StrListClear( hpaio->lengthMeasurementList );
        StrListAdd( hpaio->lengthMeasurementList,
                         STR_LENGTH_MEASUREMENT_UNKNOWN );
        if( hpaio->scannerType == SCANNER_TYPE_PML )
        {
            StrListAdd( hpaio->lengthMeasurementList,
                             STR_LENGTH_MEASUREMENT_UNLIMITED );
        }
        StrListAdd( hpaio->lengthMeasurementList,
                         STR_LENGTH_MEASUREMENT_APPROXIMATE );
        StrListAdd( hpaio->lengthMeasurementList,
                         STR_LENGTH_MEASUREMENT_PADDED );
        /* TODO: hpaioStrListAdd(hpaio->lengthMeasurementList,
          STR_LENGTH_MEASUREMENT_EXACT); */
    }

    /* OPTION_TL_X, OPTION_TL_Y, OPTION_BR_X, OPTION_BR_Y: */
    if( initValues )
    {
        hpaioSetDefaultValue( hpaio, OPTION_TL_X );
        hpaioSetDefaultValue( hpaio, OPTION_TL_Y );
        hpaioSetDefaultValue( hpaio, OPTION_BR_X );
        hpaioSetDefaultValue( hpaio, OPTION_BR_Y );
        reload |= SANE_INFO_RELOAD_OPTIONS;
        goto processGeometry;
    }
    else if( option == OPTION_TL_X ||
             option == OPTION_TL_Y ||
             option == OPTION_BR_X ||
             option == OPTION_BR_Y )
    {
        processGeometry : hpaio->effectiveTlx = hpaio->currentTlx;
        hpaio->effectiveBrx = hpaio->currentBrx;
        FIX_GEOMETRY( hpaio->effectiveTlx,
                      hpaio->effectiveBrx,
                      hpaio->brxRange.min,
                      hpaio->brxRange.max );
        hpaio->effectiveTly = hpaio->currentTly;
        hpaio->effectiveBry = hpaio->currentBry;
        FIX_GEOMETRY( hpaio->effectiveTly,
                      hpaio->effectiveBry,
                      hpaio->bryRange.min,
                      hpaio->bryRange.max );
        reload |= SANE_INFO_RELOAD_PARAMS;
    }
    if( ( hpaio->currentLengthMeasurement != LENGTH_MEASUREMENT_UNLIMITED ) !=
        ( ( hpaio->option[OPTION_BR_Y].cap & SANE_CAP_INACTIVE ) == 0 ) )
    {
        if( hpaio->currentLengthMeasurement == LENGTH_MEASUREMENT_UNLIMITED )
        {
            hpaio->option[OPTION_BR_Y].cap |= SANE_CAP_INACTIVE;
        }
        else
        {
            hpaio->option[OPTION_BR_Y].cap &= ~SANE_CAP_INACTIVE;
        }
        reload |= SANE_INFO_RELOAD_OPTIONS;
    }

    /* Pre-scan parameters: */
    if( reload & SANE_INFO_RELOAD_PARAMS )
    {
        switch( hpaio->currentScanMode )
        {
            case SCAN_MODE_LINEART:
                hpaio->prescanParameters.format = SANE_FRAME_GRAY;
                hpaio->prescanParameters.depth = 1;
                break;

            case SCAN_MODE_GRAYSCALE:
                hpaio->prescanParameters.format = SANE_FRAME_GRAY;
                hpaio->prescanParameters.depth = 8;
                break;

            case SCAN_MODE_COLOR:
            default:
                hpaio->prescanParameters.format = SANE_FRAME_RGB;
                hpaio->prescanParameters.depth = 8;
                break;
        }
        hpaio->prescanParameters.last_frame = SANE_TRUE;

        
        hpaio->prescanParameters.lines = MILLIMETERS_TO_PIXELS( hpaio->effectiveBry - hpaio->effectiveTly,
                                                                hpaio->currentResolution );
        
        hpaio->prescanParameters.pixels_per_line = MILLIMETERS_TO_PIXELS( hpaio->effectiveBrx - hpaio->effectiveTlx,
                                                                          hpaio->currentResolution );

        hpaio->prescanParameters.bytes_per_line = BYTES_PER_LINE( hpaio->prescanParameters.pixels_per_line,
                                                                  hpaio->prescanParameters.depth * ( hpaio->prescanParameters.format ==
                                                                                                     SANE_FRAME_RGB ?
                                                                                                     3 :
                                                                                                     1 ) );
    }

    return reload;
}

static void hpaioSetupOptions( hpaioScanner_t hpaio )
{
    hpaio->option[OPTION_NUM_OPTIONS].name = SANE_NAME_NUM_OPTIONS;
    hpaio->option[OPTION_NUM_OPTIONS].title = SANE_TITLE_NUM_OPTIONS;
    hpaio->option[OPTION_NUM_OPTIONS].desc = SANE_DESC_NUM_OPTIONS;
    hpaio->option[OPTION_NUM_OPTIONS].type = SANE_TYPE_INT;
    hpaio->option[OPTION_NUM_OPTIONS].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_NUM_OPTIONS].size = sizeof( SANE_Int );
    hpaio->option[OPTION_NUM_OPTIONS].cap = SANE_CAP_SOFT_DETECT;
    hpaio->option[OPTION_NUM_OPTIONS].constraint_type = SANE_CONSTRAINT_NONE;

    hpaio->option[GROUP_SCAN_MODE].title = "Scan mode";
    hpaio->option[GROUP_SCAN_MODE].type = SANE_TYPE_GROUP;

    hpaio->option[OPTION_SCAN_MODE].name = SANE_NAME_SCAN_MODE;
    hpaio->option[OPTION_SCAN_MODE].title = SANE_TITLE_SCAN_MODE;
    hpaio->option[OPTION_SCAN_MODE].desc = SANE_DESC_SCAN_MODE;
    hpaio->option[OPTION_SCAN_MODE].type = SANE_TYPE_STRING;
    hpaio->option[OPTION_SCAN_MODE].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_SCAN_MODE].size = LEN_STRING_OPTION_VALUE;
    hpaio->option[OPTION_SCAN_MODE].cap = SANE_CAP_SOFT_SELECT |
                                          SANE_CAP_SOFT_DETECT;
    hpaio->option[OPTION_SCAN_MODE].constraint_type = SANE_CONSTRAINT_STRING_LIST;
    hpaio->option[OPTION_SCAN_MODE].constraint.string_list = hpaio->scanModeList;

    hpaio->option[OPTION_SCAN_RESOLUTION].name = SANE_NAME_SCAN_RESOLUTION;
    hpaio->option[OPTION_SCAN_RESOLUTION].title = SANE_TITLE_SCAN_RESOLUTION;
    hpaio->option[OPTION_SCAN_RESOLUTION].desc = SANE_DESC_SCAN_RESOLUTION;
    hpaio->option[OPTION_SCAN_RESOLUTION].type = SANE_TYPE_INT;
    hpaio->option[OPTION_SCAN_RESOLUTION].unit = SANE_UNIT_DPI;
    hpaio->option[OPTION_SCAN_RESOLUTION].size = sizeof( SANE_Int );
    hpaio->option[OPTION_SCAN_RESOLUTION].cap = SANE_CAP_SOFT_SELECT |
                                                SANE_CAP_SOFT_DETECT;
    hpaio->option[OPTION_SCAN_RESOLUTION].constraint_type = SANE_CONSTRAINT_RANGE;
    hpaio->option[OPTION_SCAN_RESOLUTION].constraint.range = &hpaio->resolutionRange;
    hpaio->resolutionRange.quant = 0;

    hpaio->option[GROUP_ADVANCED].title = "Advanced";
    hpaio->option[GROUP_ADVANCED].type = SANE_TYPE_GROUP;
    hpaio->option[GROUP_ADVANCED].cap = SANE_CAP_ADVANCED;

    hpaio->option[OPTION_CONTRAST].name = SANE_NAME_CONTRAST;
    hpaio->option[OPTION_CONTRAST].title = SANE_TITLE_CONTRAST;
    hpaio->option[OPTION_CONTRAST].desc = SANE_DESC_CONTRAST;
    hpaio->option[OPTION_CONTRAST].type = SANE_TYPE_INT;
    hpaio->option[OPTION_CONTRAST].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_CONTRAST].size = sizeof( SANE_Int );
    hpaio->option[OPTION_CONTRAST].cap = SANE_CAP_SOFT_SELECT |
                                         SANE_CAP_SOFT_DETECT |
                                         SANE_CAP_ADVANCED |
                                         SANE_CAP_INACTIVE;
    hpaio->option[OPTION_CONTRAST].constraint_type = SANE_CONSTRAINT_RANGE;
    hpaio->option[OPTION_CONTRAST].constraint.range = &hpaio->contrastRange;
    hpaio->contrastRange.min = PML_CONTRAST_MIN;
    hpaio->contrastRange.max = PML_CONTRAST_MAX;
    hpaio->contrastRange.quant = 0;
    hpaio->defaultContrast = PML_CONTRAST_DEFAULT;

    hpaio->option[OPTION_COMPRESSION].name = "compression";
    hpaio->option[OPTION_COMPRESSION].title = "Compression";
    hpaio->option[OPTION_COMPRESSION].desc = "Selects the scanner compression method for faster scans, "
                                                             "possibly at the expense of image quality.";
    hpaio->option[OPTION_COMPRESSION].type = SANE_TYPE_STRING;
    hpaio->option[OPTION_COMPRESSION].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_COMPRESSION].size = LEN_STRING_OPTION_VALUE;
    hpaio->option[OPTION_COMPRESSION].cap = SANE_CAP_SOFT_SELECT |
                                            SANE_CAP_SOFT_DETECT |
                                            SANE_CAP_ADVANCED;
    hpaio->option[OPTION_COMPRESSION].constraint_type = SANE_CONSTRAINT_STRING_LIST;
    hpaio->option[OPTION_COMPRESSION].constraint.string_list = hpaio->compressionList;

    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].name = "jpeg-compression-factor";
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].title = "JPEG compression factor";
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].desc = "Sets the scanner JPEG compression factor.  "
                                                                                     "Larger numbers mean better compression, and "
                                                                                     "smaller numbers mean better image quality.";
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].type = SANE_TYPE_INT;
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].size = sizeof( SANE_Int );
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].cap = SANE_CAP_SOFT_SELECT |
                                                        SANE_CAP_SOFT_DETECT |
                                                        SANE_CAP_ADVANCED;
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].constraint_type = SANE_CONSTRAINT_RANGE;
    hpaio->option[OPTION_JPEG_COMPRESSION_FACTOR].constraint.range = &hpaio->jpegCompressionFactorRange;
    hpaio->jpegCompressionFactorRange.min = MIN_JPEG_COMPRESSION_FACTOR;
    hpaio->jpegCompressionFactorRange.max = MAX_JPEG_COMPRESSION_FACTOR;
    hpaio->jpegCompressionFactorRange.quant = 0;
    hpaio->defaultJpegCompressionFactor = SAFER_JPEG_COMPRESSION_FACTOR;

    hpaio->option[OPTION_BATCH_SCAN].name = "batch-scan";
    hpaio->option[OPTION_BATCH_SCAN].title = "Batch scan";
    hpaio->option[OPTION_BATCH_SCAN].desc = "Guarantees that a \"no documents\" condition will be "
                                                           "returned after the last scanned page, to prevent "
                                                           "endless flatbed scans after a batch scan.  "
                                                           "For some models, option changes in the middle of a batch "
                                                           "scan don't take effect until after the last page.";
    hpaio->option[OPTION_BATCH_SCAN].type = SANE_TYPE_BOOL;
    hpaio->option[OPTION_BATCH_SCAN].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_BATCH_SCAN].size = sizeof( SANE_Bool );
    hpaio->option[OPTION_BATCH_SCAN].cap = SANE_CAP_SOFT_SELECT |
                                           SANE_CAP_SOFT_DETECT |
                                           SANE_CAP_ADVANCED;
    hpaio->option[OPTION_BATCH_SCAN].constraint_type = SANE_CONSTRAINT_NONE;

    hpaio->option[OPTION_ADF_MODE].name = "source";  // xsane expects this.
    hpaio->option[OPTION_ADF_MODE].title = "Source";
    hpaio->option[OPTION_ADF_MODE].desc = "Selects the desired scan source for models with both "
                                                     "flatbed and automatic document feeder (ADF) capabilities.  "
                                                     "The \"Auto\" setting means that the ADF will be used "
                                                     "if it's loaded, and the flatbed (if present) will be "
                                                     "used otherwise.";
    hpaio->option[OPTION_ADF_MODE].type = SANE_TYPE_STRING;
    hpaio->option[OPTION_ADF_MODE].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_ADF_MODE].size = LEN_STRING_OPTION_VALUE;
    hpaio->option[OPTION_ADF_MODE].cap = SANE_CAP_SOFT_SELECT |
                                         SANE_CAP_SOFT_DETECT |
                                         SANE_CAP_ADVANCED;
    hpaio->option[OPTION_ADF_MODE].constraint_type = SANE_CONSTRAINT_STRING_LIST;
    hpaio->option[OPTION_ADF_MODE].constraint.string_list = hpaio->adfModeList;

    hpaio->option[OPTION_DUPLEX].name = "duplex";
    hpaio->option[OPTION_DUPLEX].title = "Duplex";
    hpaio->option[OPTION_DUPLEX].desc = "Enables scanning on both sides of the page for models "
                                                   "with duplex-capable document feeders.  For pages printed "
                                                   "in \"book\"-style duplex mode, one side will be scanned "
                                                   "upside-down.  This feature is experimental.";
    hpaio->option[OPTION_DUPLEX].type = SANE_TYPE_BOOL;
    hpaio->option[OPTION_DUPLEX].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_DUPLEX].size = sizeof( SANE_Bool );
    hpaio->option[OPTION_DUPLEX].cap = SANE_CAP_SOFT_SELECT |
                                       SANE_CAP_SOFT_DETECT |
                                       SANE_CAP_ADVANCED;
    hpaio->option[OPTION_DUPLEX].constraint_type = SANE_CONSTRAINT_NONE;

    hpaio->option[GROUP_GEOMETRY].title = "Geometry";
    hpaio->option[GROUP_GEOMETRY].type = SANE_TYPE_GROUP;
    hpaio->option[GROUP_GEOMETRY].cap = SANE_CAP_ADVANCED;

    hpaio->option[OPTION_LENGTH_MEASUREMENT].name = "length-measurement";
    hpaio->option[OPTION_LENGTH_MEASUREMENT].title = "Length measurement";
    hpaio->option[OPTION_LENGTH_MEASUREMENT].desc = "Selects how the scanned image length is measured and "
                                                                           "reported, which is impossible to know in advance for "
                                                                           "scrollfed scans.";
    hpaio->option[OPTION_LENGTH_MEASUREMENT].type = SANE_TYPE_STRING;
    hpaio->option[OPTION_LENGTH_MEASUREMENT].unit = SANE_UNIT_NONE;
    hpaio->option[OPTION_LENGTH_MEASUREMENT].size = LEN_STRING_OPTION_VALUE;
    hpaio->option[OPTION_LENGTH_MEASUREMENT].cap = SANE_CAP_SOFT_SELECT |
                                                   SANE_CAP_SOFT_DETECT |
                                                   SANE_CAP_ADVANCED;
    hpaio->option[OPTION_LENGTH_MEASUREMENT].constraint_type = SANE_CONSTRAINT_STRING_LIST;
    hpaio->option[OPTION_LENGTH_MEASUREMENT].constraint.string_list = hpaio->lengthMeasurementList;

    hpaio->option[OPTION_TL_X].name = SANE_NAME_SCAN_TL_X;
    hpaio->option[OPTION_TL_X].title = SANE_TITLE_SCAN_TL_X;
    hpaio->option[OPTION_TL_X].desc = SANE_DESC_SCAN_TL_X;
    hpaio->option[OPTION_TL_X].type = GEOMETRY_OPTION_TYPE;
    hpaio->option[OPTION_TL_X].unit = SANE_UNIT_MM;
    hpaio->option[OPTION_TL_X].size = sizeof( SANE_Int );
    hpaio->option[OPTION_TL_X].cap = SANE_CAP_SOFT_SELECT |
                                     SANE_CAP_SOFT_DETECT;
    hpaio->option[OPTION_TL_X].constraint_type = SANE_CONSTRAINT_RANGE;
    hpaio->option[OPTION_TL_X].constraint.range = &hpaio->tlxRange;
    hpaio->tlxRange.min = 0;
    hpaio->tlxRange.quant = 0;

    hpaio->option[OPTION_TL_Y].name = SANE_NAME_SCAN_TL_Y;
    hpaio->option[OPTION_TL_Y].title = SANE_TITLE_SCAN_TL_Y;
    hpaio->option[OPTION_TL_Y].desc = SANE_DESC_SCAN_TL_Y;
    hpaio->option[OPTION_TL_Y].type = GEOMETRY_OPTION_TYPE;
    hpaio->option[OPTION_TL_Y].unit = SANE_UNIT_MM;
    hpaio->option[OPTION_TL_Y].size = sizeof( SANE_Int );
    hpaio->option[OPTION_TL_Y].cap = SANE_CAP_SOFT_SELECT |
                                     SANE_CAP_SOFT_DETECT;
    hpaio->option[OPTION_TL_Y].constraint_type = SANE_CONSTRAINT_RANGE;
    hpaio->option[OPTION_TL_Y].constraint.range = &hpaio->tlyRange;
    hpaio->tlyRange.min = 0;
    hpaio->tlyRange.quant = 0;

    hpaio->option[OPTION_BR_X].name = SANE_NAME_SCAN_BR_X;
    hpaio->option[OPTION_BR_X].title = SANE_TITLE_SCAN_BR_X;
    hpaio->option[OPTION_BR_X].desc = SANE_DESC_SCAN_BR_X;
    hpaio->option[OPTION_BR_X].type = GEOMETRY_OPTION_TYPE;
    hpaio->option[OPTION_BR_X].unit = SANE_UNIT_MM;
    hpaio->option[OPTION_BR_X].size = sizeof( SANE_Int );
    hpaio->option[OPTION_BR_X].cap = SANE_CAP_SOFT_SELECT |
                                     SANE_CAP_SOFT_DETECT;
    hpaio->option[OPTION_BR_X].constraint_type = SANE_CONSTRAINT_RANGE;
    hpaio->option[OPTION_BR_X].constraint.range = &hpaio->brxRange;
    hpaio->brxRange.min = 0;
    hpaio->brxRange.quant = 0;

    hpaio->option[OPTION_BR_Y].name = SANE_NAME_SCAN_BR_Y;
    hpaio->option[OPTION_BR_Y].title = SANE_TITLE_SCAN_BR_Y;
    hpaio->option[OPTION_BR_Y].desc = SANE_DESC_SCAN_BR_Y;
    hpaio->option[OPTION_BR_Y].type = GEOMETRY_OPTION_TYPE;
    hpaio->option[OPTION_BR_Y].unit = SANE_UNIT_MM;
    hpaio->option[OPTION_BR_Y].size = sizeof( SANE_Int );
    hpaio->option[OPTION_BR_Y].cap = SANE_CAP_SOFT_SELECT |
                                     SANE_CAP_SOFT_DETECT;
    hpaio->option[OPTION_BR_Y].constraint_type = SANE_CONSTRAINT_RANGE;
    hpaio->option[OPTION_BR_Y].constraint.range = &hpaio->bryRange;
    hpaio->bryRange.min = 0;
    hpaio->bryRange.quant = 0;
}

int hpaioSclSendCommandCheckError( hpaioScanner_t hpaio, int cmd, int param )
{
    SANE_Status retcode;

    SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_CLEAR_ERROR_STACK, 0 );

    retcode = SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, cmd, param );
    
    if( retcode == SANE_STATUS_GOOD &&
        ( ( cmd != SCL_CMD_CHANGE_DOCUMENT && cmd != SCL_CMD_UNLOAD_DOCUMENT ) ||
          hpaio->beforeScan ) )
    {
        retcode = hpaioScannerToSaneError( hpaio );
    }

    return retcode;
}

static SANE_Status hpaioProgramOptions( hpaioScanner_t hpaio )
{
    DBG( 0,  "\nhpaio: hpaioProgramOptions()\n" ); 

    hpaio->effectiveScanMode = hpaio->currentScanMode;
    hpaio->effectiveResolution = hpaio->currentResolution;

    //    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    //    {
        /* Set output data type and width. */
        switch( hpaio->currentScanMode )
        {
            case SCAN_MODE_LINEART:
                SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                                SCL_CMD_SET_OUTPUT_DATA_TYPE,
                                SCL_DATA_TYPE_LINEART );
                SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                                SCL_CMD_SET_DATA_WIDTH,
                                SCL_DATA_WIDTH_LINEART );
                break;
            
            case SCAN_MODE_GRAYSCALE:
                SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                                SCL_CMD_SET_OUTPUT_DATA_TYPE,
                                SCL_DATA_TYPE_GRAYSCALE );
                SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                                SCL_CMD_SET_DATA_WIDTH,
                                SCL_DATA_WIDTH_GRAYSCALE );
                break;
            
            case SCAN_MODE_COLOR:
            default:
                SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                                SCL_CMD_SET_OUTPUT_DATA_TYPE,
                                SCL_DATA_TYPE_COLOR );
                SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                                SCL_CMD_SET_DATA_WIDTH,
                                SCL_DATA_WIDTH_COLOR );
                break;
        }

        /* Set MFPDTF. */
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_MFPDTF,
                        hpaio->mfpdtf ? SCL_MFPDTF_ON : SCL_MFPDTF_OFF );

//BREAKPOINT;
        /* Set compression. */
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_COMPRESSION,
                        ( hpaio->currentCompression ==
                          COMPRESSION_JPEG ? SCL_COMPRESSION_JPEG : SCL_COMPRESSION_NONE ) );

        /* Set JPEG compression factor. */
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_JPEG_COMPRESSION_FACTOR,
                        hpaio->currentJpegCompressionFactor );

        /* Set X and Y resolution. */
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_X_RESOLUTION,
                        hpaio->currentResolution );
        
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_Y_RESOLUTION,
                        hpaio->currentResolution );

        /* Set X and Y position and extent. */
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_X_POSITION,
                        MILLIMETERS_TO_DECIPIXELS( hpaio->effectiveTlx ) );
        
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_Y_POSITION,
                        MILLIMETERS_TO_DECIPIXELS( hpaio->effectiveTly ) );
        
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_X_EXTENT,
                        MILLIMETERS_TO_DECIPIXELS( hpaio->effectiveBrx -
                                                   hpaio->effectiveTlx ) );
                                                   
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_SET_Y_EXTENT,
                        MILLIMETERS_TO_DECIPIXELS( hpaio->effectiveBry -
                                                   hpaio->effectiveTly ) );

        /* Download color map to OfficeJet Pro 11xx. */
        if( hpaio->scl.compat & ( SCL_COMPAT_1150 | SCL_COMPAT_1170 ) )
        {
            SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                            SCL_CMD_SET_DOWNLOAD_TYPE,
                            SCL_DOWNLOAD_TYPE_COLORMAP );
            
            SclSendCommand( hpaio->deviceid, hpaio->scan_channelid,
                            SCL_CMD_DOWNLOAD_BINARY_DATA,
                            sizeof( hp11xxSeriesColorMap ) );
            
            hplip_WriteHP( hpaio->deviceid, hpaio->scan_channelid,
                          ( char * ) hp11xxSeriesColorMap,
                          sizeof( hp11xxSeriesColorMap ) );
        }

        /* For OfficeJet R and PSC 500 series, set CCD resolution to 600
         * for lineart. */
        if( hpaio->scl.compat & SCL_COMPAT_R_SERIES &&
            hpaio->currentScanMode == SCAN_MODE_LINEART )
        {
            SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, 
                            SCL_CMD_SET_CCD_RESOLUTION, 600 );
        }

    return SANE_STATUS_GOOD;
}

static SANE_Status hpaioAdvanceDocument( hpaioScanner_t hpaio )
{
//BREAKPOINT;
    
    SANE_Status retcode;
    int documentLoaded = 0;

    DBG( 0,  "\nhpaio: hpaioAdvanceDocument:\n"
                    "beforeScan=%d, already{Pre,Post}AdvancedDocument={%d,%d}, "
                    "noDocsConditionPending=%d, "
                    "currentPageNumber=%d, currentSideNumber=%d.\n",
                    hpaio->beforeScan,
                    hpaio->alreadyPreAdvancedDocument,
                    hpaio->alreadyPostAdvancedDocument,
                    hpaio->noDocsConditionPending,
                    hpaio->currentPageNumber,
                    hpaio->currentSideNumber );

    if( hpaio->beforeScan )
    {
        hpaio->alreadyPostAdvancedDocument = 0;
        retcode = hpaioScannerToSaneStatus( hpaio );
        if( retcode != SANE_STATUS_GOOD || hpaio->alreadyPreAdvancedDocument )
        {
            goto abort;
        }
        hpaio->alreadyPreAdvancedDocument = 1;
    }
    else
    {
        if( hpaio->alreadyPostAdvancedDocument )
        {
            retcode = SANE_STATUS_GOOD;
            goto abort;
        }
        hpaio->alreadyPreAdvancedDocument = 0;
        hpaio->alreadyPostAdvancedDocument = 1;
    }

    //    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    //    {

        retcode = SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                              SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                              SCL_INQ_ADF_DOCUMENT_LOADED,
                              &documentLoaded,
                              0,
                              0 );
                              
        if( retcode != SANE_STATUS_GOOD && 
            retcode != SANE_STATUS_UNSUPPORTED )
        {
            goto abort;
        }

        if( hpaio->currentSideNumber == 1 )
        {
            if( hpaio->currentDuplex )
            {
                /* Duplex change side. */
                retcode = hpaioSclSendCommandCheckError( hpaio,
                                                    SCL_CMD_CHANGE_DOCUMENT,
                                                    SCL_CHANGE_DOC_DUPLEX_SIDE );
                                                    
                if( retcode != SANE_STATUS_GOOD )
                {
                    goto abort;
                }
                
                hpaio->alreadyPreAdvancedDocument = 1;
                hpaio->currentSideNumber = 2;
            }
            else if( hpaio->scl.unloadAfterScan && !hpaio->beforeScan )
            {
                /* Unload document. */
                retcode = hpaioSclSendCommandCheckError( hpaio,
                                                    SCL_CMD_UNLOAD_DOCUMENT,
                                                    0 );
                if( retcode != SANE_STATUS_GOOD )
                {
                    goto abort;
                }
                hpaio->currentSideNumber = 0;
                if( !documentLoaded )
                {
                    goto noDocs;
                }
            }
            else if( documentLoaded )
            {
                goto changeDoc;
            }
            else
            {
                unloadDoc:
                /* Unload document. */
                retcode = hpaioSclSendCommandCheckError( hpaio,
                                                    SCL_CMD_UNLOAD_DOCUMENT,
                                                    0 );
                if( retcode != SANE_STATUS_GOOD )
                {
                    goto abort;
                }
                goto noDocs;
            }
        }
        else if( hpaio->currentSideNumber == 2 )
        {
            /* Duplex change side. */
            retcode = hpaioSclSendCommandCheckError( hpaio,
                                                SCL_CMD_CHANGE_DOCUMENT,
                                                SCL_CHANGE_DOC_DUPLEX_SIDE );
            if( retcode != SANE_STATUS_GOOD )
            {
                goto abort;
            }
            if( documentLoaded )
            {
                goto changeDoc;
            }
            goto unloadDoc;
        }
        else /* if (!hpaio->currentSideNumber) */
        {
            if( documentLoaded &&
                hpaio->beforeScan &&
                hpaio->currentAdfMode != ADF_MODE_FLATBED )
            {
                changeDoc:
                if( hpaio->currentDuplex )
                {
                    /* Duplex change document. */
                    retcode = hpaioSclSendCommandCheckError( hpaio,
                                                        SCL_CMD_CHANGE_DOCUMENT,
                                                        SCL_CHANGE_DOC_DUPLEX );
                }
                else
                {
                    /* Simplex change document. */
                    retcode = hpaioSclSendCommandCheckError( hpaio,
                                                        SCL_CMD_CHANGE_DOCUMENT,
                                                        SCL_CHANGE_DOC_SIMPLEX );
                }
                if( retcode != SANE_STATUS_GOOD )
                {
                    goto abort;
                }
                hpaio->alreadyPreAdvancedDocument = 1;
                hpaio->currentPageNumber++;
                hpaio->currentSideNumber = 1;
            }
            else
            {
                noDocs:
                hpaio->currentPageNumber = 0;
                hpaio->currentSideNumber = 0;
                if( hpaio->beforeScan )
                {
                    if( hpaio->currentAdfMode == ADF_MODE_ADF )
                    {
                        retcode = SANE_STATUS_NO_DOCS;
                        goto abort;
                    }
                }
                else if( hpaio->currentBatchScan )
                {
                    if( hpaio->endOfData )
                    {
                        hpaio->noDocsConditionPending = 1;
                    }
                    retcode = SANE_STATUS_NO_DOCS;
                    goto abort;
                }
            }
        }

        if( !hpaio->beforeScan && !hpaio->currentPageNumber )
        {
            retcode = SANE_STATUS_NO_DOCS;
            goto abort;
        }

    if( !hpaio->beforeScan && !hpaio->endOfData )
    {
        retcode = SANE_STATUS_NO_DOCS;
        goto abort;
    }

    retcode = SANE_STATUS_GOOD;
    abort:
    DBG( 0,  "hpaio: hpaioAdvanceDocument returns %d:\n"
                    "beforeScan=%d, already{Pre,Post}AdvancedDocument={%d,%d}, "
                    "noDocsConditionPending=%d, "
                    "currentPageNumber=%d, currentSideNumber=%d.\n",
                    retcode,
                    hpaio->beforeScan,
                    hpaio->alreadyPreAdvancedDocument,
                    hpaio->alreadyPostAdvancedDocument,
                    hpaio->noDocsConditionPending,
                    hpaio->currentPageNumber,
                    hpaio->currentSideNumber );

    if( retcode != SANE_STATUS_GOOD )
    {
        hpaio->alreadyPreAdvancedDocument = 0;
        hpaio->alreadyPostAdvancedDocument = 0;
        hpaio->currentPageNumber = 0;
        hpaio->currentSideNumber = 0;
    }
    return retcode;
}

/******************************************************* SANE API *******************************************************/

extern SANE_Status sane_hpaio_init( SANE_Int * pVersionCode,
                                    SANE_Auth_Callback authorize )
{
    //DBG_INIT();
    DBG( 0, "\nsane_hpaio_init() *******************************************************************************************\n" );
    
    hplip_Init();

    //hpaioDeviceListReset();
    //ResetDevices( hpaioDeviceList );
    //InitDevices( hpaioDeviceList );
    //hpaioDeviceList = InitDevices();
    
    if( pVersionCode )
    {
        *pVersionCode = SANE_VERSION_CODE( 1, 0, 6 );
    }

    return SANE_STATUS_GOOD;
}

extern SANE_Status sane_hpaio_get_devices( const SANE_Device *** ppDeviceList,
                                           SANE_Bool localOnly )
{
    DBG( 0,  "\nhpaio: sane_hpaio_get_devices()\n" );

    //__asm("int3");
    ResetDevices( &hpaioDeviceList );
    //hpaioDeviceList = NULL;
    
    ProbeDevices( &hpaioDeviceList );

    *ppDeviceList = ( const SANE_Device ** ) hpaioDeviceList;
    return SANE_STATUS_GOOD;
}

extern SANE_Status sane_hpaio_get_parameters( SANE_Handle handle,
                                              SANE_Parameters * pParams )
{
    DBG( 0,  "\nhpaio: sane_hpaio_get_parameters()\n" );
    
    hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;
    char * s = "";
    if( !hpaio->hJob )
    {
        *pParams = hpaio->prescanParameters;
        s = "pre";
    }
    else
    {
        *pParams = hpaio->scanParameters;
    }
    DBG( 0,  "hpaio: sane_hpaio_get_parameters(%sscan): "
                    "format=%d, last_frame=%d, lines=%d, depth=%d, "
                    "pixels_per_line=%d, bytes_per_line=%d.\n",
                    s,
                    pParams->format,
                    pParams->last_frame,
                    pParams->lines,
                    pParams->depth,
                    pParams->pixels_per_line,
                    pParams->bytes_per_line );
    return SANE_STATUS_GOOD;
}

extern const SANE_Option_Descriptor * sane_hpaio_get_option_descriptor( SANE_Handle handle,
                                                                        SANE_Int option )
{
    hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;
    DBG( 0,  "hpaio: sane_hpaio_get_option_descriptor(option=%d)\n",
                    option );
    if( option < 0 || option >= OPTION_LAST )
    {
        return 0;
    }
    DBG( 0,  "hpaio: option=%d name=<%s>\n"
                    "\ttype=%d unit=%d size=%d cap=0x%2.2X ctype=%d\n",
                    option,
                    hpaio->option[option].name,
                    hpaio->option[option].type,
                    hpaio->option[option].unit,
                    hpaio->option[option].size,
                    hpaio->option[option].cap,
                    hpaio->option[option].constraint_type );
    if( hpaio->option[option].constraint_type == SANE_CONSTRAINT_RANGE )
    {
        DBG( 0,  "\tmin=%d=0x%8.8X, max=%d=0x%8.8X, quant=%d\n",
                        hpaio->option[option].constraint.range->min,
                        hpaio->option[option].constraint.range->min,
                        hpaio->option[option].constraint.range->max,
                        hpaio->option[option].constraint.range->max,
                        hpaio->option[option].constraint.range->quant );
    }

    return &hpaio->option[option];
}

extern SANE_Status sane_hpaio_control_option( SANE_Handle handle,
                                              SANE_Int option,
                                              SANE_Action action,
                                              void * pValue,
                                              SANE_Int * pInfo )
{
    hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;
    SANE_Int _info;
    SANE_Int * pIntValue = pValue;
    SANE_String pStrValue = pValue;
    SANE_Status retcode;

    if( !pInfo )
    {
        pInfo = &_info;
    }
    DBG( 0,  "\nhpaio: sane_hpaio_control_option(option=%d,"
                    "action=%d)\n",
                    option,
                    action );

    switch( action )
    {
        case SANE_ACTION_GET_VALUE:
            switch( option )
            {
                case OPTION_NUM_OPTIONS:
                    *pIntValue = OPTION_LAST;
                    break;

                case OPTION_SCAN_MODE:
                    switch( hpaio->currentScanMode )
                    {
                        case SCAN_MODE_LINEART:
                            strcpy( pStrValue, STR_SCAN_MODE_LINEART );
                            break;
                        case SCAN_MODE_GRAYSCALE:
                            strcpy( pStrValue, STR_SCAN_MODE_GRAYSCALE );
                            break;
                        case SCAN_MODE_COLOR:
                            strcpy( pStrValue, STR_SCAN_MODE_COLOR );
                            break;
                        default:
                            strcpy( pStrValue, STR_UNKNOWN );
                            break;
                    }
                    break;

                case OPTION_SCAN_RESOLUTION:
                    *pIntValue = hpaio->currentResolution;
                    break;

                case OPTION_CONTRAST:
                    *pIntValue = hpaio->currentContrast;
                    break;

                case OPTION_COMPRESSION:
                    switch( hpaio->currentCompression )
                    {
                        case COMPRESSION_NONE:
                            strcpy( pStrValue, STR_COMPRESSION_NONE );
                            break;
                        case COMPRESSION_MH:
                            strcpy( pStrValue, STR_COMPRESSION_MH );
                            break;
                        case COMPRESSION_MR:
                            strcpy( pStrValue, STR_COMPRESSION_MR );
                            break;
                        case COMPRESSION_MMR:
                            strcpy( pStrValue, STR_COMPRESSION_MMR );
                            break;
                        case COMPRESSION_JPEG:
                            strcpy( pStrValue, STR_COMPRESSION_JPEG );
                            break;
                        default:
                            strcpy( pStrValue, STR_UNKNOWN );
                            break;
                    }
                    break;

                case OPTION_JPEG_COMPRESSION_FACTOR:
                    *pIntValue = hpaio->currentJpegCompressionFactor;
                    break;

                case OPTION_BATCH_SCAN:
                    *pIntValue = hpaio->currentBatchScan;
                    break;

                case OPTION_ADF_MODE:
                    switch( hpaio->currentAdfMode )
                    {
                        case ADF_MODE_AUTO:
                            strcpy( pStrValue, STR_ADF_MODE_AUTO );
                            break;
                        case ADF_MODE_FLATBED:
                            strcpy( pStrValue, STR_ADF_MODE_FLATBED );
                            break;
                        case ADF_MODE_ADF:
                            strcpy( pStrValue, STR_ADF_MODE_ADF );
                            break;
                        default:
                            strcpy( pStrValue, STR_UNKNOWN );
                            break;
                    }
                    break;

                case OPTION_DUPLEX:
                    *pIntValue = hpaio->currentDuplex;
                    break;

                case OPTION_LENGTH_MEASUREMENT:
                    switch( hpaio->currentLengthMeasurement )
                    {
                        case LENGTH_MEASUREMENT_UNKNOWN:
                            strcpy( pStrValue, STR_LENGTH_MEASUREMENT_UNKNOWN );
                            break;
                        case LENGTH_MEASUREMENT_UNLIMITED:
                            strcpy( pStrValue,
                                    STR_LENGTH_MEASUREMENT_UNLIMITED );
                            break;
                        case LENGTH_MEASUREMENT_APPROXIMATE:
                            strcpy( pStrValue,
                                    STR_LENGTH_MEASUREMENT_APPROXIMATE );
                            break;
                        case LENGTH_MEASUREMENT_PADDED:
                            strcpy( pStrValue, STR_LENGTH_MEASUREMENT_PADDED );
                            break;
                        case LENGTH_MEASUREMENT_EXACT:
                            strcpy( pStrValue, STR_LENGTH_MEASUREMENT_EXACT );
                            break;
                        default:
                            strcpy( pStrValue, STR_UNKNOWN );
                            break;
                    }
                    break;

                case OPTION_TL_X:
                    *pIntValue = hpaio->currentTlx;
                    break;

                case OPTION_TL_Y:
                    *pIntValue = hpaio->currentTly;
                    break;

                case OPTION_BR_X:
                    *pIntValue = hpaio->currentBrx;
                    break;

                case OPTION_BR_Y:
                    *pIntValue = hpaio->currentBry;
                    break;

                default:
                    return SANE_STATUS_INVAL;
            }
            break;

        case SANE_ACTION_SET_VALUE:
            if( hpaio->option[option].cap & SANE_CAP_INACTIVE )
            {
                return SANE_STATUS_INVAL;
            }
            switch( option )
            {
                case OPTION_SCAN_MODE:
                    if( !strcasecmp( pStrValue, STR_SCAN_MODE_LINEART ) &&
                        hpaio->supportsScanMode[SCAN_MODE_LINEART] )
                    {
                        hpaio->currentScanMode = SCAN_MODE_LINEART;
                        break;
                    }
                    if( !strcasecmp( pStrValue, STR_SCAN_MODE_GRAYSCALE ) &&
                        hpaio->supportsScanMode[SCAN_MODE_GRAYSCALE] )
                    {
                        hpaio->currentScanMode = SCAN_MODE_GRAYSCALE;
                        break;
                    }
                    if( !strcasecmp( pStrValue, STR_SCAN_MODE_COLOR ) &&
                        hpaio->supportsScanMode[SCAN_MODE_COLOR] )
                    {
                        hpaio->currentScanMode = SCAN_MODE_COLOR;
                        break;
                    }
                    return SANE_STATUS_INVAL;

                case OPTION_SCAN_RESOLUTION:
                    if( ( hpaio->option[option].constraint_type ==
                          SANE_CONSTRAINT_WORD_LIST &&
                          !NumListIsInList( ( SANE_Int * )hpaio->option[option].constraint.word_list, *pIntValue ) ) ||
                          ( hpaio->option[option].constraint_type == SANE_CONSTRAINT_RANGE &&
                          ( *pIntValue<hpaio->resolutionRange.min ||
                            *pIntValue>hpaio->resolutionRange.max ) ) )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentResolution = *pIntValue;
                    break;

                case OPTION_CONTRAST:
                    if( *pIntValue<hpaio->contrastRange.min ||
                        *pIntValue>hpaio->contrastRange.max )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentContrast = *pIntValue;
                    break;

                case OPTION_COMPRESSION:
                    {
                        int supportedCompression = hpaio->supportsScanMode[hpaio->currentScanMode];
                        if( !strcasecmp( pStrValue, STR_COMPRESSION_NONE ) &&
                            supportedCompression & COMPRESSION_NONE )
                        {
                            hpaio->currentCompression = COMPRESSION_NONE;
                            break;
                        }
                        if( !strcasecmp( pStrValue, STR_COMPRESSION_MH ) &&
                            supportedCompression & COMPRESSION_MH )
                        {
                            hpaio->currentCompression = COMPRESSION_MH;
                            break;
                        }
                        if( !strcasecmp( pStrValue, STR_COMPRESSION_MR ) &&
                            supportedCompression & COMPRESSION_MR )
                        {
                            hpaio->currentCompression = COMPRESSION_MR;
                            break;
                        }
                        if( !strcasecmp( pStrValue, STR_COMPRESSION_MMR ) &&
                            supportedCompression & COMPRESSION_MMR )
                        {
                            hpaio->currentCompression = COMPRESSION_MMR;
                            break;
                        }
                        if( !strcasecmp( pStrValue, STR_COMPRESSION_JPEG ) &&
                            supportedCompression & COMPRESSION_JPEG )
                        {
                            hpaio->currentCompression = COMPRESSION_JPEG;
                            break;
                        }
                        return SANE_STATUS_INVAL;
                    }

                case OPTION_JPEG_COMPRESSION_FACTOR:
                    if( *pIntValue<MIN_JPEG_COMPRESSION_FACTOR ||
                        *pIntValue>MAX_JPEG_COMPRESSION_FACTOR )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentJpegCompressionFactor = *pIntValue;
                    break;

                case OPTION_BATCH_SCAN:
                    if( *pIntValue != SANE_FALSE && *pIntValue != SANE_TRUE )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentBatchScan = *pIntValue;
                    break;

                case OPTION_ADF_MODE:
                    if( !strcasecmp( pStrValue, STR_ADF_MODE_AUTO ) &&
                        hpaio->supportedAdfModes & ADF_MODE_AUTO )
                    {
                        hpaio->currentAdfMode = ADF_MODE_AUTO;
                        break;
                    }
                    if( !strcasecmp( pStrValue, STR_ADF_MODE_FLATBED ) &&
                        hpaio->supportedAdfModes & ADF_MODE_FLATBED )
                    {
                        hpaio->currentAdfMode = ADF_MODE_FLATBED;
                        break;
                    }
                    if( !strcasecmp( pStrValue, STR_ADF_MODE_ADF ) &&
                        hpaio->supportedAdfModes & ADF_MODE_ADF )
                    {
                        hpaio->currentAdfMode = ADF_MODE_ADF;
                        break;
                    }
                    return SANE_STATUS_INVAL;

                case OPTION_DUPLEX:
                    if( *pIntValue != SANE_FALSE && *pIntValue != SANE_TRUE )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentDuplex = *pIntValue;
                    break;

                case OPTION_LENGTH_MEASUREMENT:
                    if( !strcasecmp( pStrValue,
                                     STR_LENGTH_MEASUREMENT_UNKNOWN ) )
                    {
                        hpaio->currentLengthMeasurement = LENGTH_MEASUREMENT_UNKNOWN;
                        break;
                    }
                    if( !strcasecmp( pStrValue,
                                     STR_LENGTH_MEASUREMENT_UNLIMITED ) )
                    {
                        if( hpaio->scannerType != SCANNER_TYPE_PML )
                        {
                            return SANE_STATUS_INVAL;
                        }
                        hpaio->currentLengthMeasurement = LENGTH_MEASUREMENT_UNLIMITED;
                        break;
                    }
                    if( !strcasecmp( pStrValue,
                                     STR_LENGTH_MEASUREMENT_APPROXIMATE ) )
                    {
                        hpaio->currentLengthMeasurement = LENGTH_MEASUREMENT_APPROXIMATE;
                        break;
                    }
                    if( !strcasecmp( pStrValue, STR_LENGTH_MEASUREMENT_PADDED ) )
                    {
                        hpaio->currentLengthMeasurement = LENGTH_MEASUREMENT_PADDED;
                        break;
                    }
                    if( !strcasecmp( pStrValue, STR_LENGTH_MEASUREMENT_EXACT ) )
                    {
                        hpaio->currentLengthMeasurement = LENGTH_MEASUREMENT_EXACT;
                        break;
                    }
                    return SANE_STATUS_INVAL;

                case OPTION_TL_X:
                    if( *pIntValue<hpaio->tlxRange.min ||
                        *pIntValue>hpaio->tlxRange.max )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentTlx = *pIntValue;
                    break;

                case OPTION_TL_Y:
                    if( *pIntValue<hpaio->tlyRange.min ||
                        *pIntValue>hpaio->tlyRange.max )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentTly = *pIntValue;
                    break;

                case OPTION_BR_X:
                    if( *pIntValue<hpaio->brxRange.min ||
                        *pIntValue>hpaio->brxRange.max )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentBrx = *pIntValue;
                    break;

                case OPTION_BR_Y:
                    if( *pIntValue<hpaio->bryRange.min ||
                        *pIntValue>hpaio->bryRange.max )
                    {
                        return SANE_STATUS_INVAL;
                    }
                    hpaio->currentBry = *pIntValue;
                    break;

                default:
                    return SANE_STATUS_INVAL;
            }
            goto reload;

        case SANE_ACTION_SET_AUTO:
            retcode = hpaioSetDefaultValue( hpaio, option );
            if( retcode != SANE_STATUS_GOOD )
            {
                return retcode;
            }
            reload : *pInfo = hpaioUpdateDescriptors( hpaio, option );
            DBG( 0,  "hpaio: sane_hpaio_control_option(option=%d,"
                            "action=%d): info=0x%2.2X\n",
                            option,
                            action,
                            *pInfo );
            break;

        default:
            return SANE_STATUS_INVAL;
    }

    if( ( action == SANE_ACTION_GET_VALUE || action == SANE_ACTION_SET_VALUE ) && pValue )
    {
        if( hpaio->option[option].type == SANE_TYPE_STRING )
        {
            DBG( 0,  "hpaio: %s option %d = <%s>\n",
                            ( action == SANE_ACTION_SET_VALUE ? "set " : "" ),
                            option,
                            (char *)pValue );
        }
        else
        {
            DBG( 0,  "hpaio: %s option %d = %d = 0x%8.8X\n",
                            hpaio->saneDevice.name,
                            ( action == SANE_ACTION_SET_VALUE ? "set " : "" ),
                            option,
                            *( int * ) pValue,
                            *( int * ) pValue );
        }
    }

    return SANE_STATUS_GOOD;
}


extern SANE_Status sane_hpaio_open( SANE_String_Const devicename,
                                    SANE_Handle * pHandle )
{
    DBG( 0,  "\nhpaio:sane_hpaio_open(%s) *******************************************************************************************\n", devicename );
    
    SANE_Status retcode = SANE_STATUS_INVAL;
    hpaioScanner_t hpaio = 0;
    int r;
    char deviceIDString[LEN_DEVICE_ID_STRING];
    char model[256];
    int forceJpegForGrayAndColor = 0;
    int force300dpiForLineart = 0;
    int force300dpiForGrayscale = 0;
    int supportsMfpdtf = 1;
    char devname[256];
    MsgAttributes ma;

    hpaio = hpaioFindScanner( devicename );
    
    if( hpaio )
    {
        goto done;     /* reuse same device, why?? (des) */
    }
    
    hpaio = malloc( sizeof( struct hpaioScanner_s ) );
    
    if( !hpaio )
    {
        retcode = SANE_STATUS_NO_MEM;
        goto abort;
    }

    hpaioAddScanner( hpaio );
    
    if( pHandle )
    {
        *pHandle = hpaio;
    }
    
    memset( hpaio, 0, sizeof( struct hpaioScanner_s ) );
    
    /* add hp: back onto URI that was removed previously */
    if(strncmp(devicename, "hp:", 3) != 0)
    {
        sprintf( devname, "hp:%s", devicename );
    }
    else
    {
        strcpy( devname, devicename );
    }

    DBG( 0, "Opening %s...\n", devname );
    
    hplip_ModelQuery(devname, &ma);  /* get device specific parameters */

    hpaio->deviceid = hplip_OpenHP( (char *)devname, &ma );
    strncpy( hpaio->deviceuri, devname, sizeof(hpaio->deviceuri) );
    
    if( hpaio->deviceid == -1 )
    {
        retcode = SANE_STATUS_IO_ERROR;
        goto abort;
    }
    
    hpaio->scan_channelid = -1;
    hpaio->cmd_channelid = -1;

    /* Get the device ID string and initialize the SANE_Device structure. */
    memset( deviceIDString, 0, LEN_DEVICE_ID_STRING );
    
    if( hplip_GetID( hpaio->deviceid,  deviceIDString, sizeof(deviceIDString)) == 0 )
    {
        retcode = SANE_STATUS_INVAL;
        goto abort;
    }
    
    DBG( 0,  "hpaio:device ID string=<%s>\n", deviceIDString );
    
    hpaio->saneDevice.name = strdup( devicename ); 
    
    hpaio->saneDevice.vendor = "Hewlett-Packard"; 
    
    hplip_GetModel( deviceIDString, model, sizeof( model ) );
    
    DBG( 0, "Model = %s\n", model );
    
    hpaio->saneDevice.model = strdup( model );
    hpaio->saneDevice.type = "multi-function peripheral";

    /* Initialize option descriptors. */
    hpaioSetupOptions( hpaio ); 

//BREAKPOINT;
    
    /* Guess the command language (SCL or PML) based on the model string. */
    if( UNDEFINED_MODEL( hpaio ) )
    {
        hpaio->scannerType = SCANNER_TYPE_SCL;
    }
    else if( strcasestr( hpaio->saneDevice.model, "laserjet" ) )
    {
        hpaio->scannerType = SCANNER_TYPE_PML;
        hpaio->pml.openFirst = 1;
        
        if( strcasecmp( hpaio->saneDevice.model, "HP_LaserJet_1100" ) == 0 )
        {
            hpaio->pml.dontResetBeforeNextNonBatchPage = 1;
        }
        else
        {
            hpaio->pml.startNextBatchPageEarly = 1;
        }
    }
    else if( strcasecmp( hpaio->saneDevice.model, "OfficeJet" ) == 0 ||
             strcasecmp( hpaio->saneDevice.model, "OfficeJet_LX" ) == 0 ||
             strcasecmp( hpaio->saneDevice.model, "OfficeJet_Series_300" ) == 0 )
    {
        hpaio->scannerType = SCANNER_TYPE_PML;
        hpaio->preDenali = 1;
    }
    else if( strcasecmp( hpaio->saneDevice.model, "OfficeJet_Series_500" ) == 0 ||
             strcasecmp( hpaio->saneDevice.model, "All-in-One_IJP-V100" ) == 0 )
    {
        hpaio->scannerType = SCANNER_TYPE_PML;
        hpaio->fromDenali = 1;
        force300dpiForLineart = 1;
        force300dpiForGrayscale = 1;
        hpaio->defaultCompression[SCAN_MODE_LINEART] = COMPRESSION_MH;
        hpaio->defaultCompression[SCAN_MODE_GRAYSCALE] = COMPRESSION_JPEG;
        hpaio->defaultJpegCompressionFactor = SAFER_JPEG_COMPRESSION_FACTOR;
    }
    else if( strcasecmp( hpaio->saneDevice.model, "OfficeJet_Series_600" ) == 0 )
    {
        hpaio->scannerType = SCANNER_TYPE_PML;
        hpaio->denali = 1;
        forceJpegForGrayAndColor = 1;
        force300dpiForLineart = 1;
        hpaio->defaultCompression[SCAN_MODE_LINEART] = COMPRESSION_MH;
        hpaio->defaultJpegCompressionFactor = SAFER_JPEG_COMPRESSION_FACTOR;
    }
    else if( strcasecmp( hpaio->saneDevice.model, "Printer/Scanner/Copier_300" ) == 0 )
    {
        hpaio->scannerType = SCANNER_TYPE_PML;
        forceJpegForGrayAndColor = 1;
        force300dpiForLineart = 1;
        hpaio->defaultCompression[SCAN_MODE_LINEART] = COMPRESSION_MH;
        hpaio->defaultJpegCompressionFactor = SAFER_JPEG_COMPRESSION_FACTOR;
    }
    else if( strcasecmp( hpaio->saneDevice.model, "OfficeJet_Series_700" ) == 0 )
    {
        hpaio->scannerType = SCANNER_TYPE_PML;
        forceJpegForGrayAndColor = 1;
        force300dpiForLineart = 1;
        hpaio->defaultCompression[SCAN_MODE_LINEART] = COMPRESSION_MH;
        hpaio->defaultJpegCompressionFactor = SAFER_JPEG_COMPRESSION_FACTOR;
    }
    else if( strcasecmp( hpaio->saneDevice.model, "OfficeJet_T_Series" ) == 0 )
    {
        hpaio->scannerType = SCANNER_TYPE_PML;
        forceJpegForGrayAndColor = 1;
    }
    else
    {
        hpaio->scannerType = SCANNER_TYPE_SCL;
    }

    DBG( 0, "Scanner type (0=SCL, 1=PML): %d\n", hpaio->scannerType );
    
    /* Open and reset scanner command channel.
     * This also allocates the PML objects if necessary. */
    
//BREAKPOINT;
    
    retcode = hpaioConnOpen( hpaio );
    
    if( retcode != SANE_STATUS_GOOD )
    {
        goto abort;
    }

    /* Probing and setup for SCL scanners... */
    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    {
        /* Even though this isn't SCANNER_TYPE_PML, there are still a few
         * interesting PML objects. */
        
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_CLEAR_ERROR_STACK, 0 );

	//        hpaio->scl.objSupportedFunctions = hpaioPmlAllocateID( hpaio, "\x1\x1\x2\x43" );
        hpaio->scl.objSupportedFunctions = hpaioPmlAllocateID( hpaio, "1.3.6.1.4.1.11.2.3.9.4.2.1.1.2.67.0" );
        /* Probe the SCL model. */
        DBG( 0,  "hpaio:Using SCL protocol.\n" );

        retcode = SclInquire( hpaio->deviceid, 
                              hpaio->scan_channelid,
                              SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                              SCL_INQ_HP_MODEL_11,
                              0,
                              hpaio->scl.compat1150,
                              LEN_MODEL_RESPONSE );
        
        if( retcode == SANE_STATUS_GOOD )
        {
            hpaio->scl.compat |= SCL_COMPAT_OFFICEJET;
        }
        else if( retcode != SANE_STATUS_UNSUPPORTED )
        {
            goto abort;
        }
        DBG( 0,  "hpaio: scl.compat1150=<%s>.\n",
                        hpaio->scl.compat1150 );

        retcode = SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                              SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                              SCL_INQ_HP_MODEL_12,
                              0,
                              hpaio->scl.compatPost1150,
                              LEN_MODEL_RESPONSE );
        
        if( retcode == SANE_STATUS_GOOD )
        {
            hpaio->scl.compat |= SCL_COMPAT_POST_1150;
        }
        else if( retcode != SANE_STATUS_UNSUPPORTED )
        {
            goto abort;
        }
        DBG( 0,  "hpaio: scl.compatPost1150=<%s>.\n",
                        hpaio->scl.compatPost1150 );

        if( !hpaio->scl.compat )
        {
            SET_DEFAULT_MODEL( hpaio, "(unknown scanner)" );
        }
        else if( hpaio->scl.compat == SCL_COMPAT_OFFICEJET )
        {
            hpaio->scl.compat |= SCL_COMPAT_1150;
            SET_DEFAULT_MODEL( hpaio, "(OfficeJet 1150)" );
        }
        else if( !strcmp( hpaio->scl.compatPost1150, "5400A" ) )
        {
            hpaio->scl.compat |= SCL_COMPAT_1170;
            SET_DEFAULT_MODEL( hpaio, "(OfficeJet 1170)" );
        }
        else if( !strcmp( hpaio->scl.compatPost1150, "5500A" ) )
        {
            hpaio->scl.compat |= SCL_COMPAT_R_SERIES;
            SET_DEFAULT_MODEL( hpaio, "(OfficeJet R Series)" );
        }
        else if( !strcmp( hpaio->scl.compatPost1150, "5600A" ) )
        {
            hpaio->scl.compat |= SCL_COMPAT_G_SERIES;
            SET_DEFAULT_MODEL( hpaio, "(OfficeJet G Series)" );
        }
        else if( !strcmp( hpaio->scl.compatPost1150, "5700A" ) )
        {
            hpaio->scl.compat |= SCL_COMPAT_K_SERIES;
            SET_DEFAULT_MODEL( hpaio, "(OfficeJet K Series)" );
        }
        else if( !strcmp( hpaio->scl.compatPost1150, "5800A" ) )
        {
            hpaio->scl.compat |= SCL_COMPAT_D_SERIES;
            SET_DEFAULT_MODEL( hpaio, "(OfficeJet D Series)" );
        }
        else if( !strcmp( hpaio->scl.compatPost1150, "5900A" ) )
        {
            hpaio->scl.compat |= SCL_COMPAT_6100_SERIES;
            SET_DEFAULT_MODEL( hpaio, "(OfficeJet 6100 Series)" );
        }
        else
        {
            SET_DEFAULT_MODEL( hpaio, "(unknown OfficeJet)" );
        }
        DBG( 0,  "hpaio: scl.compat=0x%4.4X.\n",
                        hpaio->scl.compat );

        /* Decide which position/extent unit to use.  "Device pixels" works
         * better on most models, but the 1150 requires "decipoints." */
        if( hpaio->scl.compat & ( SCL_COMPAT_1150 ) )
        {
            hpaio->scl.decipixelChar = SCL_CHAR_DECIPOINTS;
            hpaio->decipixelsPerInch = DECIPOINTS_PER_INCH;
        }
        else
        {
            hpaio->scl.decipixelChar = SCL_CHAR_DEVPIXELS;
            hpaio->decipixelsPerInch = DEVPIXELS_PER_INCH;
            /* Check for non-default decipixelsPerInch definition. */
            SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                        SCL_INQ_DEVICE_PIXELS_PER_INCH,
                        &hpaio->decipixelsPerInch,
                        0,
                        0 );
        }
        DBG( 0,  "hpaio: decipixelChar='%c', decipixelsPerInch=%d.\n",
                        hpaio->scl.decipixelChar,
                        hpaio->decipixelsPerInch );

        /* Is MFPDTF supported? */
        if( hpaioSclSendCommandCheckError( hpaio,
                                      SCL_CMD_SET_MFPDTF,
                                      SCL_MFPDTF_ON ) != SANE_STATUS_GOOD )
        {
            DBG( 0,  "hpaio: Doesn't support MFPDTF.\n" );
            supportsMfpdtf = 0;
        }

        /* All scan modes are supported with no compression. */
        hpaio->supportsScanMode[SCAN_MODE_LINEART] = COMPRESSION_NONE;
        hpaio->supportsScanMode[SCAN_MODE_GRAYSCALE] = COMPRESSION_NONE;
        hpaio->supportsScanMode[SCAN_MODE_COLOR] = COMPRESSION_NONE;

        /* Is JPEG also supported for grayscale and color (requires MFPDTF)? */
//BREAKPOINT;        
        
        if( supportsMfpdtf )
        {
            if( hpaioSclSendCommandCheckError( hpaio,
                                          SCL_CMD_SET_COMPRESSION,
                                          SCL_COMPRESSION_JPEG ) == SANE_STATUS_GOOD )
            {
                hpaio->supportsScanMode[SCAN_MODE_GRAYSCALE] |= COMPRESSION_JPEG;
                hpaio->supportsScanMode[SCAN_MODE_COLOR] |= COMPRESSION_JPEG;
            }
        }

        /* Determine the minimum and maximum resolution.
                  * Probe for both X and Y, and pick largest min and smallest max.
                 * For the 1150, set min to 50 to prevent scan head crashes (<42). */
        SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                    SCL_CMD_INQUIRE_MINIMUM_VALUE,
                    SCL_CMD_SET_X_RESOLUTION,
                    &hpaio->scl.minXRes,
                    0,
                    0 );
        
        SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                    SCL_CMD_INQUIRE_MINIMUM_VALUE,
                    SCL_CMD_SET_Y_RESOLUTION,
                    &hpaio->scl.minYRes,
                    0,
                    0 );
        
        if( hpaio->scl.compat & SCL_COMPAT_1150 &&
            hpaio->scl.minYRes < SCL_MIN_Y_RES_1150 )
        {
            hpaio->scl.minYRes = SCL_MIN_Y_RES_1150;
        }
        r = hpaio->scl.minXRes;
        if( r < hpaio->scl.minYRes )
        {
            r = hpaio->scl.minYRes;
        }
        
        hpaio->resolutionRange.min = r;
        
        SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                    SCL_CMD_INQUIRE_MAXIMUM_VALUE,
                    SCL_CMD_SET_X_RESOLUTION,
                    &hpaio->scl.maxXRes,
                    0,
                    0 );
        
        SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                    SCL_CMD_INQUIRE_MAXIMUM_VALUE,
                    SCL_CMD_SET_Y_RESOLUTION,
                    &hpaio->scl.maxYRes,
                    0,
                   0 );
        
        r = hpaio->scl.maxXRes;
        
        if( r > hpaio->scl.maxYRes )
        {
            r = hpaio->scl.maxYRes;
        }
        
        if( hpaio->scl.compat & ( SCL_COMPAT_1150 | SCL_COMPAT_1170 ) && r > SCL_MAX_RES_1150_1170 )
        {
            r = SCL_MAX_RES_1150_1170;
        }
        hpaio->resolutionRange.max = r;

        /* Determine ADF/duplex capabilities. */
        {
            int flatbedCapability = 1;
            
            SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_INQUIRE_MAXIMUM_VALUE,
                        SCL_PSEUDO_FLATBED_Y_RESOLUTION,
                        &flatbedCapability,
                        0,
                        0 );
                        
            SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                        SCL_CMD_INQUIRE_DEVICE_PARAMETER,
                        SCL_INQ_ADF_CAPABILITY,
                        &hpaio->scl.adfCapability,
                        0,
                        0 );
            
            DBG( 0,  "hpaio: ADF capability=%d.\n",
                            hpaio->scl.adfCapability );
            
            if( !hpaio->scl.adfCapability )
            {
                hpaio->supportedAdfModes = ADF_MODE_FLATBED;
            }
            else if( hpaio->scl.compat & SCL_COMPAT_K_SERIES ||
                     !flatbedCapability )
            {
                hpaio->supportedAdfModes = ADF_MODE_ADF;
            }
            else
            {
                int supportedFunctions;

                hpaio->supportedAdfModes = ADF_MODE_AUTO |
                                           ADF_MODE_FLATBED |
                                           ADF_MODE_ADF;
                if( hpaio->scl.compat & ( SCL_COMPAT_1170 |
                                          SCL_COMPAT_R_SERIES |
                                          SCL_COMPAT_G_SERIES ) )
                {
                    hpaio->scl.unloadAfterScan = 1;
                }
                if( PmlRequestGet( hpaio->deviceid, hpaio->cmd_channelid, hpaio->scl.objSupportedFunctions ) != ERROR &&
                    PmlGetIntegerValue( hpaio->scl.objSupportedFunctions,
                                        0,
                                        &supportedFunctions ) != ERROR &&
                    supportedFunctions & PML_SUPPFUNC_DUPLEX )
                {
                    hpaio->supportsDuplex = 1;
                }
            }
        }

        /* Determine maximum X and Y extents. */
        SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                    SCL_CMD_INQUIRE_MAXIMUM_VALUE,
                    SCL_CMD_SET_X_EXTENT,
                    &hpaio->scl.maxXExtent,
                    0,
                    0 );
        
        SclInquire( hpaio->deviceid, hpaio->scan_channelid,
                    SCL_CMD_INQUIRE_MAXIMUM_VALUE,
                    SCL_CMD_SET_Y_EXTENT,
                    &hpaio->scl.maxYExtent,
                    0,
                    0 );
        
        DBG( 0,  "hpaio: Maximum extents: x=%d, y=%d.\n",
                        hpaio->scl.maxXExtent,
                        hpaio->scl.maxYExtent );
        
        hpaio->tlxRange.max = hpaio->brxRange.max = DECIPIXELS_TO_MILLIMETERS( hpaio->scl.maxXExtent );
        hpaio->tlyRange.max = hpaio->bryRange.max = DECIPIXELS_TO_MILLIMETERS( hpaio->scl.maxYExtent );

        /* Probing and setup for PML scanners... */
    }
    else /* if (hpaio->scannerType==SCANNER_TYPE_PML) */
    {
        int comps = 0;

        hpaio->decipixelsPerInch = DECIPOINTS_PER_INCH;

        /*ChannelSetSelectPollTimeout( hpaio->chan, &selectPollTimeout );
                        
                  ChannelSetSelectPollCallback( hpaio->chan,
                                                                              hpaioPmlSelectCallback,
                                                                              hpaio );*/

        /* Determine supported scan modes and compression settings. */
        if( hpaio->preDenali )
        {
            comps |= COMPRESSION_MMR;
        }
        
        //DBG( 0, "Set compression\n" );
        
        PmlSetIntegerValue( hpaio->pml.objCompression,
                            PML_TYPE_ENUMERATION,
                            PML_COMPRESSION_NONE );
        
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objCompression, 0, 0 ) != ERROR )
        {
            comps |= COMPRESSION_NONE;
        }
        
        PmlSetIntegerValue( hpaio->pml.objCompression,
                            PML_TYPE_ENUMERATION,
                            PML_COMPRESSION_MH );
        
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objCompression, 0, 0 ) != ERROR )
        {
            comps |= COMPRESSION_MH;
        }
        
        PmlSetIntegerValue( hpaio->pml.objCompression,
                            PML_TYPE_ENUMERATION,
                            PML_COMPRESSION_MR );
                            
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objCompression, 0, 0 ) != ERROR )
        {
            comps |= COMPRESSION_MR;
        }
        
        PmlSetIntegerValue( hpaio->pml.objCompression,
                            PML_TYPE_ENUMERATION,
                            PML_COMPRESSION_MMR );
        
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objCompression, 0, 0 ) != ERROR )
        {
            comps |= COMPRESSION_MMR;
        }
        
        //DBG( 0, "Set data type\n" );
        PmlSetIntegerValue( hpaio->pml.objPixelDataType,
                            PML_TYPE_ENUMERATION,
                            PML_DATA_TYPE_LINEART );
        
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objPixelDataType, 0, 0 ) != ERROR )
        {
            hpaio->supportsScanMode[SCAN_MODE_LINEART] = comps;
        }
            comps &= COMPRESSION_NONE;
        
        if( forceJpegForGrayAndColor )
        {
            comps = 0;
        }
        
        PmlSetIntegerValue( hpaio->pml.objCompression,
                            PML_TYPE_ENUMERATION,
                            PML_COMPRESSION_JPEG );
                            
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objCompression, 0, 0 ) != ERROR )
        {
            comps |= COMPRESSION_JPEG;
        }
        
        PmlSetIntegerValue( hpaio->pml.objPixelDataType,
                            PML_TYPE_ENUMERATION,
                            PML_DATA_TYPE_GRAYSCALE );
        
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objPixelDataType, 0, 0 ) != ERROR )
        {
            hpaio->supportsScanMode[SCAN_MODE_GRAYSCALE] = comps;
        }
        
        PmlSetIntegerValue( hpaio->pml.objPixelDataType,
                            PML_TYPE_ENUMERATION,
                            PML_DATA_TYPE_COLOR );
        
        if( PmlRequestSetRetry( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objPixelDataType, 0, 0 ) != ERROR )
        {
            hpaio->supportsScanMode[SCAN_MODE_COLOR] = comps;
        }

        /* Determine supported resolutions. */
        NumListClear( hpaio->resolutionList );
        NumListClear( hpaio->lineartResolutionList );
        
        if( hpaio->preDenali )
        {
            NumListAdd( hpaio->lineartResolutionList, 200 );
            if( !strcmp( hpaio->saneDevice.model, "OfficeJet_Series_300" ) )
            {
                NumListAdd( hpaio->lineartResolutionList, 300 );
            }
            hpaio->option[OPTION_SCAN_RESOLUTION].constraint_type = SANE_CONSTRAINT_WORD_LIST;
        }
        else if( PmlRequestGet( hpaio->deviceid, hpaio->cmd_channelid, 
                                hpaio->pml.objResolutionRange ) == ERROR )
        {
pmlDefaultResRange:
            /* TODO: What are the correct X and Y resolution ranges
             * for the OfficeJet T series? */
            hpaio->resolutionRange.min = 75;
            hpaio->resolutionRange.max = 600;
        }
        else
        {
            char resList[PML_MAX_VALUE_LEN + 1];
            int i, len, res, consumed;

            PmlGetStringValue( hpaio->pml.objResolutionRange,
                               0,
                               resList,
                               PML_MAX_VALUE_LEN );
            
            resList[PML_MAX_VALUE_LEN] = 0;
            len = strlen( resList );

            /* Parse "(100)x(100),(150)x(150),(200)x(200),(300)x(300)".
                             * This isn't quite the right way to do it, but it'll do. */
            for( i = 0; i < len; )
            {
                if( resList[i] < '0' || resList[i] > '9' )
                {
                    i++;
                    continue;
                }
                if( sscanf( resList + i, "%d%n", &res, &consumed ) != 1 )
                {
                    break;
                }
                i += consumed;
                if( !force300dpiForGrayscale || res >= 300 )
                {
                    NumListAdd( hpaio->resolutionList, res );
                }
                if( !force300dpiForLineart || res >= 300 )
                {
                    NumListAdd( hpaio->lineartResolutionList, res );
                }
            }

            if( !NumListGetCount( hpaio->resolutionList ) )
            {
                goto pmlDefaultResRange;
            }
            hpaio->option[OPTION_SCAN_RESOLUTION].constraint_type = SANE_CONSTRAINT_WORD_LIST;
        }

        /* Determine contrast support. */
        if( PmlRequestGet( hpaio->deviceid, hpaio->cmd_channelid, 
                           hpaio->pml.objContrast ) != ERROR )
        {
            hpaio->option[OPTION_CONTRAST].cap &= ~SANE_CAP_INACTIVE;
        }

        /* Determine supported ADF modes. */
        if( PmlRequestGet( hpaio->deviceid, hpaio->cmd_channelid, 
                           hpaio->pml.objModularHardware ) != ERROR )
        {
            int modularHardware = 0;
            hpaio->pml.flatbedCapability = 1;
            if( PmlGetIntegerValue( hpaio->pml.objModularHardware,
                                    0,
                                    &modularHardware ) != ERROR &&
                modularHardware & PML_MODHW_ADF )
            {
                goto adfAndAuto;
            }
            
            hpaio->supportedAdfModes = ADF_MODE_FLATBED;
        }
        else
        {
adfAndAuto:
            hpaio->supportedAdfModes = ADF_MODE_AUTO | ADF_MODE_ADF;
        }
            hpaio->supportsDuplex = 0;

        hpaio->tlxRange.max = hpaio->brxRange.max = INCHES_TO_MILLIMETERS( PML_MAX_WIDTH_INCHES );
        hpaio->tlyRange.max = hpaio->bryRange.max = INCHES_TO_MILLIMETERS( PML_MAX_HEIGHT_INCHES );

    }  /* if( hpaio->scannerType == SCANNER_TYPE_SCL ) */

    DBG( 0,  "hpaio: forceJpegForGrayAndColor=%d.\n",
                    forceJpegForGrayAndColor );
    DBG( 0,  "hpaio: force300dpiForLineart=%d.\n",
                    force300dpiForLineart );
    DBG( 0,  "hpaio: force300dpiForGrayscale=%d.\n",
                    force300dpiForGrayscale );
    DBG( 0,  "hpaio: pml.openFirst=%d.\n",
                    hpaio->pml.openFirst );
    DBG( 0,  "hpaio: fromDenali=%d.\n",
                    hpaio->fromDenali );
    DBG( 0,  "hpaio: supportsScanMode: lineart=0x%2.2X, "
                    "grayscale=0x%2.2X, color=0x%2.2X.\n",
                    hpaio->supportsScanMode[SCAN_MODE_LINEART],
                    hpaio->supportsScanMode[SCAN_MODE_GRAYSCALE],
                    hpaio->supportsScanMode[SCAN_MODE_COLOR] );
    DBG( 0,  "hpaio: supportedAdfModes=0x%2.2X.\n",
                    hpaio->supportedAdfModes );
    DBG( 0,  "hpaio: supportsDuplex=%d.\n",
                    hpaio->supportsDuplex );
    DBG( 0, "hpaio: supports MFPDTF=%d\n", 
                    supportsMfpdtf );

//BREAKPOINT;

    /* Allocate MFPDTF parser if supported. */
    if( supportsMfpdtf )
    {
        hpaio->mfpdtf = MfpdtfAllocate( hpaio->deviceid, hpaio->scan_channelid );
        MfpdtfSetChannel( hpaio->mfpdtf, hpaio->scan_channelid );
        
        if( hpaio->preDenali )
        {
            MfpdtfReadSetSimulateImageHeaders( hpaio->mfpdtf, 1 );
        }
    }

done:
    /* Finish setting up option descriptors. */
    hpaioUpdateDescriptors( hpaio, OPTION_FIRST );

    if( pHandle )
    {
        *pHandle = hpaio;
    }
    //ptalDeviceSetAppInfo( dev, hpaio );
    retcode = SANE_STATUS_GOOD;

abort:
    if( hpaio )
    {
        hpaioConnClose( hpaio );
    }
    if( retcode != SANE_STATUS_GOOD )
    {
        if( hpaio )
        {
            if( hpaio->saneDevice.vendor )
            {
                free( ( void * ) hpaio->saneDevice.vendor );
            }
            if( hpaio->saneDevice.model )
            {
                free( ( void * ) hpaio->saneDevice.model );
            }
            free( hpaio );
        }
    }
    return retcode;
}

extern void sane_hpaio_cancel( SANE_Handle handle )
{
    hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;

    DBG( 0,  "\nhpaio: sane_hpaio_cancel() *******************************************************************************************\n" ); 

    if (hpaio->scannerType==SCANNER_TYPE_PML)
    {
        pml_cancel(hpaio);
        return ;
    }

    /* TODO: convert to scl_cancel. des */

    if( hpaio->mfpdtf )
    {
        MfpdtfLogToFile( hpaio->mfpdtf, 0 );
        //MfpdtfDeallocate( hpaio->mfpdtf );
    }
    
    if( hpaio->hJob )
    {
        ipClose( hpaio->hJob );
        hpaio->hJob = 0;
    }
    
    if( hpaioAdvanceDocument( hpaio ) != SANE_STATUS_GOOD )
    {
        hpaioConnEndScan( hpaio );
    }
    
} // sane_hpaio_cancel()


extern SANE_Status sane_hpaio_start( SANE_Handle handle )
{
    hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;
    SANE_Status retcode;
    IP_IMAGE_TRAITS traits;
    IP_XFORM_SPEC xforms[IP_MAX_XFORMS], * pXform = xforms;
    WORD wResult;
    
    DBG( 0,  "\nhpaio: sane_hpaio_start() ******************************************************************************************* \n" );
    
    hpaio->endOfData = 0;

    if (hpaio->scannerType==SCANNER_TYPE_PML)
        return pml_start(hpaio);

    /* TODO: convert to scl_start. des */

    /* If we just scanned the last page of a batch scan, then return the obligatory SANE_STATUS_NO_DOCS condition. */
    if( hpaio->noDocsConditionPending )
    {
        hpaio->noDocsConditionPending = 0;
        retcode = SANE_STATUS_NO_DOCS;
        goto abort;
    }

    /* Open scanner command channel. */
    retcode = hpaioConnPrepareScan( hpaio );
    
    if( retcode != SANE_STATUS_GOOD )
    {
        goto abort;
    }

    /* Change document if needed. */
    hpaio->beforeScan = 1;
    retcode = hpaioAdvanceDocument( hpaio );
    hpaio->beforeScan = 0;
    
    if( retcode != SANE_STATUS_GOOD )
    {
        goto abort;
    }

    /* Program options. */
    retcode = hpaioProgramOptions( hpaio );
    
    if( retcode != SANE_STATUS_GOOD )
    {
        goto abort;
    }

    hpaio->scanParameters = hpaio->prescanParameters;
    memset( xforms, 0, sizeof( xforms ) );
    traits.iPixelsPerRow = -1;
    
    switch( hpaio->effectiveScanMode )
    {
        case SCAN_MODE_LINEART:
            hpaio->scanParameters.format = SANE_FRAME_GRAY;
            hpaio->scanParameters.depth = 1;
            traits.iBitsPerPixel = 1;
            break;
        case SCAN_MODE_GRAYSCALE:
            hpaio->scanParameters.format = SANE_FRAME_GRAY;
            hpaio->scanParameters.depth = 8;
            traits.iBitsPerPixel = 8;
            break;
        case SCAN_MODE_COLOR:
        default:
            hpaio->scanParameters.format = SANE_FRAME_RGB;
            hpaio->scanParameters.depth = 8;
            traits.iBitsPerPixel = 24;
            break;
    }
    traits.lHorizDPI = hpaio->effectiveResolution << 16;
    traits.lVertDPI = hpaio->effectiveResolution << 16;
    traits.lNumRows = -1;
    traits.iNumPages = 1;
    traits.iPageNum = 1;

    //    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    //    {
        int lines, pixelsPerLine;

        /* Inquire exact image dimensions. */
        if( SclInquire( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_INQUIRE_DEVICE_PARAMETER, SCL_INQ_NUMBER_OF_SCAN_LINES,
                        &lines, 0, 0 ) == SANE_STATUS_GOOD )
        {
            traits.lNumRows = lines;
        }
        SclInquire( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_INQUIRE_DEVICE_PARAMETER, SCL_INQ_PIXELS_PER_SCAN_LINE,
                    &pixelsPerLine, 0, 0 );
        
        traits.iPixelsPerRow = pixelsPerLine;

        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_CLEAR_ERROR_STACK, 0 );

        /* Start scanning. */
        SclSendCommand( hpaio->deviceid, hpaio->scan_channelid, SCL_CMD_SCAN_WINDOW, 0 );

    if( hpaio->mfpdtf )
    {
        MfpdtfSetChannel( hpaio->mfpdtf, hpaio->scan_channelid );

        //MfpdtfReadSetTimeout( hpaio->mfpdtf, MFPDTF_EARLY_READ_TIMEOUT );
        MfpdtfReadStart( hpaio->mfpdtf );  /* inits mfpdtf */
        
#ifdef HPAIO_DEBUG
        int log_output=1;
#else
        int log_output=0;
#endif        

        if( log_output )
        {
            char f[256];
            static int cnt=0;   
            
            sprintf(f, "/tmp/mfpdtf_%d.out", cnt++);
            
            bug("saving raw image to %s \n", f );
            
            MfpdtfLogToFile( hpaio->mfpdtf,  f );
        }
        else
        {
            MfpdtfLogToFile( hpaio->mfpdtf,  0 );
        }
        
        while( 1 )
        {
            int rService, sopEncoding;

            rService = MfpdtfReadService( hpaio->mfpdtf );
            
            if( retcode != SANE_STATUS_GOOD )
            {
                goto abort;
            }
            
            if( rService & MFPDTF_RESULT_ERROR_MASK )
            {
                retcode = SANE_STATUS_IO_ERROR;
                goto abort;
            }

            if( rService & MFPDTF_RESULT_NEW_VARIANT_HEADER && hpaio->preDenali )
            {
                union MfpdtfVariantHeader_u vheader;
                MfpdtfReadGetVariantHeader( hpaio->mfpdtf, &vheader, sizeof( vheader ) );
                
                traits.iPixelsPerRow = LEND_GET_SHORT( vheader.faxArtoo.pixelsPerRow );
                traits.iBitsPerPixel = 1;
                
                switch( vheader.faxArtoo.dataCompression )
                {
                    case MFPDTF_RASTER_MH:
                        sopEncoding = MFPDTF_RASTER_MH;
                        break;
                    case MFPDTF_RASTER_MR:
                        sopEncoding = MFPDTF_RASTER_MR;
                        break;
                    case MFPDTF_RASTER_MMR:
                    default:
                        sopEncoding = MFPDTF_RASTER_MMR;
                        break;
                }
                goto setupDecoder;
            }
            else if( rService & MFPDTF_RESULT_NEW_START_OF_PAGE_RECORD )
            {
                struct MfpdtfImageStartPageRecord_s sop;

                if( hpaio->scannerType == SCANNER_TYPE_SCL )
                {
                    if( hpaio->currentCompression == COMPRESSION_NONE )
                    {
                        goto rawDecode;
                    }
                    else /* if (hpaio->currentCompression==COMPRESSION_JPEG) */
                    {
                        goto jpegDecode;
                    }
                }

                /* Read SOP record and set image pipeline input traits. */
                MfpdtfReadGetStartPageRecord( hpaio->mfpdtf, &sop, sizeof( sop ) );
                
                traits.iPixelsPerRow = LEND_GET_SHORT( sop.black.pixelsPerRow );
                traits.iBitsPerPixel = LEND_GET_SHORT( sop.black.bitsPerPixel );
                traits.lHorizDPI = LEND_GET_LONG( sop.black.xres );
                traits.lVertDPI = LEND_GET_LONG( sop.black.yres );
                sopEncoding = sop.encoding;
setupDecoder:
                
                /* Set up image-processing pipeline. */
                switch( sopEncoding )
                {
                    case MFPDTF_RASTER_MH:
                        pXform->aXformInfo[IP_FAX_FORMAT].dword = IP_FAX_MH;
                        goto faxDecode;
                    
                    case MFPDTF_RASTER_MR:
                        pXform->aXformInfo[IP_FAX_FORMAT].dword = IP_FAX_MR;
                        goto faxDecode;
                    
                    case MFPDTF_RASTER_MMR:
                        pXform->aXformInfo[IP_FAX_FORMAT].dword = IP_FAX_MMR;
faxDecode: 
                        ADD_XFORM( X_FAX_DECODE );
                        break;

                    case MFPDTF_RASTER_BITMAP:
                    case MFPDTF_RASTER_GRAYMAP:
                    case MFPDTF_RASTER_RGB:
rawDecode: 
                    break;

                    case MFPDTF_RASTER_JPEG:
jpegDecode:
                        pXform->aXformInfo[IP_JPG_DECODE_FROM_DENALI].dword = hpaio->fromDenali;
                        ADD_XFORM( X_JPG_DECODE );

                        pXform->aXformInfo[IP_CNV_COLOR_SPACE_WHICH_CNV].dword = IP_CNV_YCC_TO_SRGB;
                        pXform->aXformInfo[IP_CNV_COLOR_SPACE_GAMMA].dword = 0x00010000;
                        ADD_XFORM( X_CNV_COLOR_SPACE );
                        break;

                    case MFPDTF_RASTER_YCC411:
                    case MFPDTF_RASTER_PCL:
                    case MFPDTF_RASTER_NOT:
                    default:
                        /* Skip processing for unknown encodings. */
                        bug("unknown image encoding sane_start: name=%s sop=%d\n", hpaio->saneDevice.name,sopEncoding);
                }
                continue;
            }

            if( rService & MFPDTF_RESULT_IMAGE_DATA_PENDING )
            {
                /*MfpdtfReadSetTimeout( hpaio->mfpdtf, MFPDTF_LATER_READ_TIMEOUT );*/
                break;
            }
        }
    }
    hpaio->scanParameters.pixels_per_line = traits.iPixelsPerRow;
    hpaio->scanParameters.lines = traits.lNumRows;
    
    if( hpaio->scanParameters.lines < 0 )
    {
        hpaio->scanParameters.lines = MILLIMETERS_TO_PIXELS( hpaio->bryRange.max,
                                                             hpaio->effectiveResolution );
    }

    //    if( hpaio->scannerType == SCANNER_TYPE_SCL )
    //    {
        /* We have to invert bilevel data from SCL scanners. */
        if( hpaio->effectiveScanMode == SCAN_MODE_LINEART )
        {
            ADD_XFORM( X_INVERT );
        }
        else /* if (hpaio->effectiveScanMode==SCAN_MODE_COLOR) */
        {
            /* Do gamma correction on OfficeJet Pro 11xx. */
            if( hpaio->scl.compat & ( SCL_COMPAT_1150 | SCL_COMPAT_1170 ) )
            {
                pXform->aXformInfo[IP_TABLE_WHICH].dword = IP_TABLE_USER;
                pXform->aXformInfo[IP_TABLE_OPTION].pvoid = ( char * )hp11xxSeriesGammaTable;
                ADD_XFORM( X_TABLE );
            }
        }

    if( hpaio->currentLengthMeasurement == LENGTH_MEASUREMENT_PADDED )
    {
        pXform->aXformInfo[IP_PAD_LEFT].dword = 0;
        pXform->aXformInfo[IP_PAD_RIGHT].dword = 0;
        pXform->aXformInfo[IP_PAD_TOP].dword = 0;
        pXform->aXformInfo[IP_PAD_BOTTOM].dword = 0;
        pXform->aXformInfo[IP_PAD_VALUE].dword = ( hpaio->effectiveScanMode == SCAN_MODE_LINEART ) ? PAD_VALUE_LINEART : PAD_VALUE_GRAYSCALE_COLOR;
        pXform->aXformInfo[IP_PAD_MIN_HEIGHT].dword = hpaio->scanParameters.lines;
        ADD_XFORM( X_PAD );
    }

    /* If we didn't set up any xforms by now, then add the dummy "skel" xform to simplify our subsequent code path. */
    if( pXform == xforms )
    {
        ADD_XFORM( X_SKEL );
    }

    wResult = ipOpen( pXform - xforms, xforms, 0, &hpaio->hJob );
    
    if( wResult != IP_DONE || !hpaio->hJob )
    {
        retcode = SANE_STATUS_INVAL;
        goto abort;
    }

    traits.iComponentsPerPixel = ( ( traits.iBitsPerPixel % 3 ) ? 1 : 3 );
    wResult = ipSetDefaultInputTraits( hpaio->hJob, &traits );
    
    if( wResult != IP_DONE )
    {
        retcode = SANE_STATUS_INVAL;
        goto abort;
    }

    hpaio->scanParameters.bytes_per_line = BYTES_PER_LINE( hpaio->scanParameters.pixels_per_line,
                                hpaio->scanParameters.depth * ( hpaio->scanParameters.format == SANE_FRAME_RGB ? 3 : 1 ) );
    
    hpaio->totalBytesRemaining = hpaio->scanParameters.bytes_per_line * hpaio->scanParameters.lines;
    hpaio->bufferOffset = 0;
    hpaio->bufferBytesRemaining = 0;

    if( hpaio->currentLengthMeasurement == LENGTH_MEASUREMENT_UNKNOWN || hpaio->currentLengthMeasurement == LENGTH_MEASUREMENT_UNLIMITED )
    {
        hpaio->scanParameters.lines = -1;
    }
    else if( hpaio->currentLengthMeasurement == LENGTH_MEASUREMENT_EXACT )
    {
        /* TODO: Set up spool file, scan the whole image into it,
         * and set "hpaio->scanParameters.lines" accordingly.
         * Then in sane_hpaio_read, read out of the file. */
    }

    retcode = SANE_STATUS_GOOD;

abort:

    if( retcode != SANE_STATUS_GOOD )
    {
        sane_hpaio_cancel( handle );
    }
    return retcode;
    
} //sane_hpaio_start()


extern SANE_Status sane_hpaio_read( SANE_Handle handle,
                                    SANE_Byte * data,
                                    SANE_Int maxLength,
                                    SANE_Int * pLength )
{
    hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;
    SANE_Status retcode;
    DWORD dwInputAvail;
    LPBYTE pbInputBuf;
    DWORD dwInputUsed, dwInputNextPos;
    DWORD dwOutputAvail = maxLength;
    LPBYTE pbOutputBuf = data;
    DWORD dwOutputUsed, dwOutputThisPos;
    WORD wResult;

    DBG( 0,  "\nhpaio: sane_hpaio_read(maxLength=%d) ****************************************************************************\n", maxLength );

    *pLength = 0;

    if( !hpaio->hJob )
    {
        DBG( 0,  "hpaio: sane_hpaio_read(maxLength=%d): No scan pending!\n", maxLength );
        retcode = SANE_STATUS_EOF;
        goto abort;
    }

    if (hpaio->scannerType==SCANNER_TYPE_PML)
        return pml_read(hpaio, data, maxLength, pLength);

    /* TODO: convert to scl_read. des */

needMoreData:
    if( hpaio->bufferBytesRemaining <= 0 && !hpaio->endOfData )
    {
        if( !hpaio->mfpdtf )
        {
            int r, len = hpaio->totalBytesRemaining;
            DBG( 0,  "hpaio: sane_hpaio_read: totalBytesRemaining=%d.\n", hpaio->totalBytesRemaining );
            if( len <= 0 )
            {
                hpaio->endOfData = 1;
            }
            else
            {
                if( len > LEN_BUFFER )
                {
                    len = LEN_BUFFER;
                }
                
                r = ReadChannelEx( hpaio->deviceid, 
                                   hpaio->scan_channelid, 
                                   hpaio->inBuffer, 
                                   len,
                                   EXCEPTION_TIMEOUT );
                
                if( r < 0 )
                {
                    retcode = SANE_STATUS_IO_ERROR;
                    goto abort;
                }
                hpaio->bufferBytesRemaining = r;
                hpaio->totalBytesRemaining -= r;
            }
        }
        else
        {
            // mfpdtf
                int rService;

                rService = MfpdtfReadService( hpaio->mfpdtf );
                                
                if( rService & MFPDTF_RESULT_ERROR_MASK )
                {
                    retcode = SANE_STATUS_IO_ERROR;
                    goto abort;
                }

                if( rService & MFPDTF_RESULT_IMAGE_DATA_PENDING )
                {
                    hpaio->bufferBytesRemaining = MfpdtfReadInnerBlock( hpaio->mfpdtf, hpaio->inBuffer, LEN_BUFFER );
                    
                    rService = MfpdtfReadGetLastServiceResult( hpaio->mfpdtf );
                    
                    if( rService & MFPDTF_RESULT_ERROR_MASK )
                    {
                        retcode = SANE_STATUS_IO_ERROR;
                        goto abort;
                    }
                }
                else if( rService & MFPDTF_RESULT_NEW_END_OF_PAGE_RECORD || ( rService & MFPDTF_RESULT_END_PAGE && hpaio->preDenali ))
                {
                    hpaio->endOfData = 1;
                }

        } /* if (!hpaio->mfpdtf) */

        hpaio->bufferOffset = 0;
        if( hpaio->preDenali )
        {
            ipMirrorBytes( hpaio->inBuffer, hpaio->bufferBytesRemaining );
        }

    } /* if( hpaio->bufferBytesRemaining <= 0 && !hpaio->endOfData ) */

    dwInputAvail = hpaio->bufferBytesRemaining;

    if( hpaio->bufferBytesRemaining <= 0 && hpaio->endOfData )
    {
        pbInputBuf = 0;
    }
    else
    {
        pbInputBuf = hpaio->inBuffer + hpaio->bufferOffset;
    }

    wResult = ipConvert( hpaio->hJob,
                         dwInputAvail,
                         pbInputBuf,
                         &dwInputUsed,
                         &dwInputNextPos,
                         dwOutputAvail,
                         pbOutputBuf,
                         &dwOutputUsed,
                         &dwOutputThisPos );

    DBG( 0,  "hpaio: sane_hpaio_read: "
                    "ipConvert(dwInputAvail=%d,pbInputBuf=0x%8.8X,"
                    "dwInputUsed=%d,dwInputNextPos=%d,dwOutputAvail=%d,"
                    "dwOutputUsed=%d,dwOutputThisPos=%d) returns 0x%4.4X.\n",
                    dwInputAvail,
                    pbInputBuf,
                    dwInputUsed,
                    dwInputNextPos,
                    dwOutputAvail,
                    dwOutputUsed,
                    dwOutputThisPos,
                    wResult );
    
    hpaio->bufferOffset += dwInputUsed;
    hpaio->bufferBytesRemaining -= dwInputUsed;
    *pLength = dwOutputUsed;
    
    if( wResult & ( IP_INPUT_ERROR | IP_FATAL_ERROR ) )
    {
        bug("hpaio: ipConvert error=%x\n", wResult);
        retcode = SANE_STATUS_IO_ERROR;
        goto abort;
    }
    if( !dwOutputUsed )
    {
        if( wResult & IP_DONE )
        {
            retcode = SANE_STATUS_EOF;
            goto abort;
        }
        goto needMoreData;
    }

    retcode = SANE_STATUS_GOOD;

abort:
    if(!(retcode == SANE_STATUS_GOOD || retcode == SANE_STATUS_EOF))
    {
        sane_hpaio_cancel( handle );
    }

    DBG( 0,  "hpaio: sane_hpaio_read(maxLength=%d) returns %d, "
                    "*pLength=%d\n",
                    maxLength,
                    retcode,
                    *pLength );
    return retcode;

} // sane_hpaio_read()

extern void sane_hpaio_close(SANE_Handle handle)
{
    
    hpaioScanner_t hpaio = (hpaioScanner_t) handle;

    DBG( 0,  "\nhpaio: sane_hpaio_close() *******************************************************************************************\n" ); 

    hpaioPmlDeallocateObjects(hpaio);

    /* ADF may leave channel(s) open. */  
    if (hpaio->cmd_channelid > 0)
       hpaioConnEndScan(hpaio);
    
    if (hpaio->deviceid > 0)
       hplip_CloseHP(hpaio->deviceid);
    
    /* free hpaio object?? (des) */
}

extern SANE_Status sane_hpaio_set_io_mode( SANE_Handle handle,
                                           SANE_Bool nonBlocking )
{
    /*hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;*/

    DBG( 0,  "\nhpaio: sane_hpaio_set_io_mode() unsupported!\n" );

    return SANE_STATUS_UNSUPPORTED;
}

extern SANE_Status sane_hpaio_get_select_fd( SANE_Handle handle,
                                             SANE_Int * pFd )
{
    /*hpaioScanner_t hpaio = ( hpaioScanner_t ) handle;*/

    DBG( 0,  "\nhpaio: sane_hpaio_get_select_fd() unsupported!\n" );

    return SANE_STATUS_UNSUPPORTED;
}


extern void sane_hpaio_exit( void )
{
    DBG( 0, "\nhpaio: sane_hpaio_exit() *******************************************************************************************\n" );

    ResetDevices( &hpaioDeviceList );

    hplip_Exit();
}

