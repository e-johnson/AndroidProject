////////////////////////////////////////////////////////////////////////////////
// mayaExportLayer.h
// Author     : Francesco Giordana
// Start Date : January 13, 2005
// Copyright  : (C) 2006 by Francesco Giordana
// Email      : fra.giordana@tiscali.it
////////////////////////////////////////////////////////////////////////////////
// Port to 3D Studio Max - Modified original version (maxExportLayer.h)
// Author	  : Doug Perkowski - OC3 Entertainment, Inc.
// Start Date : December 10th, 2007
////////////////////////////////////////////////////////////////////////////////
/*********************************************************************************
*                                                                                *
*   This program is free software; you can redistribute it and/or modify         *
*   it under the terms of the GNU Lesser General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or            *
*   (at your option) any later version.                                          *
*                                                                                *
**********************************************************************************/

#ifndef _MAXEXPORTLAYER_H
#define _MAXEXPORTLAYER_H

#define PRECISION 0.0001

#include "max.h"
#include "iparamb2.h"
#include "iparamm2.h"

#include "IGame.h"
#include "IGameModifier.h"

#pragma warning (disable : 4996)
#pragma warning (disable : 4267)
#pragma warning (disable : 4018)

// These come from the resource file included with wm3.h.
#define IDS_CLASS_NAME                  102
#define IDS_MORPHMTL                    39
#define IDS_MTL_MAPNAME                 45
#define IDS_MTL_BASENAME                46

// This file is not included in the max SDK directly, but in the morpher sample.
// It is required to get access to the Max Morpher.  
#include "wm3.h"

// OGRE API
// Max defines PI and OgreMath.h fails to compile as a result.
#undef PI 
#include "Ogre.h"

// This used to be contained in a file called OgreNoMemoryMacros.h, which was removed in version 1.6 of Ogre.
#ifdef OGRE_MEMORY_MACROS
#undef OGRE_MEMORY_MACROS
#undef new
#undef delete
#undef malloc
#undef calloc
#undef realloc
#undef free
#endif

#include "OgreDefaultHardwareBufferManager.h"
#define PI 3.1415926535f



// standard libraries
#include <math.h>
#include <vector>
#include <set>
#include <cassert>
#include <string>

// jcr 2012/6/11 make sure hash_map is included
#include <hash_map>
// jcr 2012/6/11 In VS2010+ hash_map is in std:: not stdext:: -- default to
//               std::
#define STD_HASH_MAP_NS std

#if (_MSC_VER < 1600)
#   undef STD_HASH_MAP_NS
#   define STD_HASH_MAP_NS stdext
#endif // (_MSC_VER < 1600)

extern TCHAR* GetString( int id );
extern HINSTANCE hInstance;

// jcr 2012/6/12 max 2013 unicode support
namespace FxOgreMaxExporter {

// The string type in max 2013 and up is std::wstring (MAX_RELEASE_R15 is the
// max 2013 define)
#if defined(MAX_RELEASE_R15)

    typedef std::wstring max_string_type;

#   define  FX_OGRE_MAX_T       _M
#   define FX_OGRE_MAX_STRICMP  _wcsicmp

#else // Prior versions (2012 and below) is std::string
    
    typedef std::string max_string_type;

#   define  FX_OGRE_MAX_T       _T
#   define FX_OGRE_MAX_STRICMP  _stricmp

#endif // defined(MAX_RELEASE_R15)

typedef std::string ogre_string_type;

namespace string_tools {
        
    // Provide a clean way to correctly convert std::wstring to std::string
    // and vice versa
    template <typename dest_type, typename src_type>
    dest_type string_cast(const src_type& src) {
        return internal::string_cast_impl<dest_type, src_type>::cast(src);
    }

    // Allow raw pointer conversions
    template <typename dest_type, typename src_type>
    dest_type string_cast( src_type* src ) {
        return internal::string_cast_impl<dest_type,
            typename internal::string_type_of<const src_type*>::wrap>::cast(src);
    }

// Hide the internal bits
namespace internal {

    // Conversion case
    template <typename dest_type, typename src_type>
    struct string_cast_impl {
        static dest_type cast( const src_type& src ) {
            // Determine the buffer size required
            int buffer_size = string_traits<src_type>::convert(src.c_str(),
                                                               NULL,
                                                               0);

            // Return an empty string if the length is zero
            if ( 0 == buffer_size ) {
                return dest_type();
            }

            std::vector<typename string_traits<dest_type>::char_type>
                buffer(buffer_size);

            string_traits<src_type>::convert(src.c_str(),
                                             &buffer[0],
                                             buffer_size);

            return dest_type(buffer.begin(), buffer.end());
        }
    };

    // Easy case: casting to the same type is just a pass-through
    template <typename dest_type>
    struct string_cast_impl<dest_type, dest_type> {
        static const dest_type& cast( const dest_type& src ) {
            return src;
        }
    };

    template <typename T>
    struct string_type_of;

    template <>
    struct string_type_of<const char*> {
        typedef std::string wrap;
    };

    template <>
    struct string_type_of<const wchar_t*> {
        typedef std::wstring wrap;
    };

    template <typename T>
    struct string_traits;

    template <>
    struct string_traits<std::string> {
        typedef char char_type;

        static int convert( LPCSTR src,
                            LPWSTR buffer,
                            int    buffer_size ) {
            return MultiByteToWideChar(CP_UTF8,
                                       0,
                                       src,
                                       -1,
                                       buffer,
                                       buffer_size);
        }
    };

    template <>
    struct string_traits<std::wstring> {
        typedef wchar_t char_type;

        static int convert( LPCWSTR src,
                            LPSTR   buffer,
                            int     buffer_size) {
            return WideCharToMultiByte(CP_ACP,
                                       0,
                                       src,
                                       -1,
                                       buffer,
                                       buffer_size,
                                       0,
                                       0);
        }
    };

} // namespace internal
} // namespace string_tools
} // namespace FxOgreMaxExporter

#endif
