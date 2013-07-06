from cffi.verifier import Verifier
from .ffi import ffi

preamble = """
    #include <librtmp/rtmp.h>
    #include <librtmp/log.h>

    /* The librtmp ABI is somewhat lacking. These functions
       help a bit. */

    void RTMP_SetSWFHash(RTMP *r, const char *swfhash,
                         uint32_t swfsize) {

        if (swfhash != NULL && swfsize > 0) {
            memcpy(r->Link.SWFHash, swfhash,
                   sizeof(r->Link.SWFHash));
            r->Link.SWFSize = swfsize;
        } else {
            r->Link.SWFSize = 0;
        }
    }

    int RTMP_GetInvokeCount(RTMP *r) {
        return r->m_numInvokes;
    }

    void RTMP_SetInvokeCount(RTMP *r, int count) {
        r->m_numInvokes = count;
    }

"""

verifier = Verifier(ffi, preamble, libraries=["rtmp"],
                    ext_package="librtmp_ffi", modulename="_binding")
