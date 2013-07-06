from cffi import FFI

__all__ = ["C", "ffi"]

ffi = FFI()

try:
    ffi.cdef("""
        typedef struct AVal {
            char *av_val;
            int av_len;
        } AVal;

        typedef ... RTMP;
        typedef ... RTMPChunk;
        typedef int RTMP_LogLevel;
        typedef void* va_list;
        typedef void (RTMP_LogCallback)(int level, const char *fmt, va_list arg);

        typedef struct RTMPPacket {
            uint8_t m_headerType;
            uint8_t m_packetType;
            uint8_t m_hasAbsTimestamp;
            int m_nChannel;
            uint32_t m_nTimeStamp;
            int32_t m_nInfoField2;
            uint32_t m_nBodySize;
            uint32_t m_nBytesRead;
            RTMPChunk *m_chunk;
            char *m_body;
        } RTMPPacket;


        RTMP * RTMP_Alloc(void);
        void RTMP_Init(RTMP *r);
        int RTMP_SetupURL(RTMP *r, char *url);

        int RTMP_ParseURL(const char *url, int *protocol, AVal *host,
                          unsigned int *port, AVal *playpath, AVal *app);

        int RTMP_Connect(RTMP *r, RTMPPacket *cp);
        int RTMP_Serve(RTMP *r);

        int RTMP_IsConnected(RTMP *r);
        int RTMP_Socket(RTMP *r);
        int RTMP_IsTimedout(RTMP *r);
        int RTMP_ReadPacket(RTMP *r, RTMPPacket *packet);
        int RTMP_SendPacket(RTMP *r, RTMPPacket *packet, int queue);
        int RTMP_ClientPacket(RTMP *r, RTMPPacket *packet);

        int RTMP_ConnectStream(RTMP *r, int seek);
        int RTMP_ReconnectStream(RTMP *r, int seekTime);
        int RTMP_SendCreateStream(RTMP *r);
        void RTMP_DeleteStream(RTMP *r);
        int RTMP_Read(RTMP *r, char *buf, int size);
        int RTMP_Write(RTMP *r, const char *buf, int size);
        int RTMP_Pause(RTMP *r, int doPause);
        int RTMP_SendSeek(RTMP *r, int dTime);

        int RTMP_LibVersion(void);
        int RTMP_SetOpt(RTMP *r, const AVal *opt, AVal *arg);
        double RTMP_GetDuration(RTMP *r);
        void RTMP_EnableWrite(RTMP *r);
        void RTMP_Close(RTMP *r);
        void RTMP_Free(RTMP *r);

        void RTMPPacket_Reset(RTMPPacket *p);
        void RTMPPacket_Dump(RTMPPacket *p);
        int RTMPPacket_Alloc(RTMPPacket *p, int nSize);
        void RTMPPacket_Free(RTMPPacket *p);


        RTMP_LogLevel RTMP_LogGetLevel(void);
        void RTMP_LogSetLevel(RTMP_LogLevel lvl);
        void RTMP_UserInterrupt(void);

        void RTMP_LogSetCallback(RTMP_LogCallback *cb);

        int RTMP_HashSWF(const char *url, unsigned int *size,
                         unsigned char *hash, int age);

        void RTMP_SetSWFHash(RTMP *r, const char *swfhash,
                             uint32_t swfsize);

        int RTMP_GetInvokeCount(RTMP *r);
        void RTMP_SetInvokeCount(RTMP *r, int count);

        int vsprintf (char *dest, const char *fmt, va_list arg);

        typedef enum {
            AMF_NUMBER = 0, AMF_BOOLEAN, AMF_STRING, AMF_OBJECT,
            AMF_MOVIECLIP,      /* reserved, not used */
            AMF_NULL, AMF_UNDEFINED, AMF_REFERENCE, AMF_ECMA_ARRAY, AMF_OBJECT_END,
            AMF_STRICT_ARRAY, AMF_DATE, AMF_LONG_STRING, AMF_UNSUPPORTED,
            AMF_RECORDSET,      /* reserved, not used */
            AMF_XML_DOC, AMF_TYPED_OBJECT,
            AMF_AVMPLUS,        /* switch to AMF3 */
            AMF_INVALID = 0xff
        } AMFDataType;

        typedef ... AMFObjectProperty;
        typedef struct AMFObject { ...; } AMFObject;

        void AMF_Dump(AMFObject * obj);

        char *AMF_EncodeString(char *output, char *outend, const AVal * str);
        char *AMF_EncodeNumber(char *output, char *outend, double dVal);
        char *AMF_EncodeBoolean(char *output, char *outend, int bVal);
        char *AMF_EncodeInt16(char *output, char *outend, short nVal);
        char *AMF_EncodeInt24(char *output, char *outend, int nVal);
        char *AMF_EncodeInt32(char *output, char *outend, int nVal);

        int AMF_Decode(AMFObject * obj, const char *pBuffer, int nSize,
                       int bDecodeName);

        int AMF_CountProp(AMFObject * obj);
        AMFObjectProperty *AMF_GetProp(AMFObject * obj, const AVal * name,
                                       int nIndex);

        AMFDataType AMFProp_GetType(AMFObjectProperty * prop);
        void AMFProp_GetName(AMFObjectProperty * prop, AVal * name);
        void AMFProp_SetName(AMFObjectProperty * prop, AVal * name);
        double AMFProp_GetNumber(AMFObjectProperty * prop);
        int AMFProp_GetBoolean(AMFObjectProperty * prop);
        void AMFProp_GetString(AMFObjectProperty * prop, AVal * str);
        void AMFProp_GetObject(AMFObjectProperty * prop, AMFObject * obj);
        int AMFProp_IsValid(AMFObjectProperty * prop);

    """)
except Exception as err:
    raise ImportError("Unable to load librtmp: {0}".format(err))

C = ffi.dlopen(None)

