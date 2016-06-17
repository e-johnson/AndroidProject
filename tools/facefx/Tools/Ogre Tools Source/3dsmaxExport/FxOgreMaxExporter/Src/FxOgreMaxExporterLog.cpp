////////////////////////////////////////////////////////////////////////////////
// FxOgreMaxExporterLog.cpp
// Author	  : Jamie Redmond - OC3 Entertainment, Inc.
// Copyright  : (C) 2007 OC3 Entertainment, Inc.
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

#include "FxOgreMaxExporterLog.h"

#include <stdio.h>
#ifdef WIN32
	#include <stdarg.h>
#else
	#include <varargs.h>
#endif

#include <iostream>
#include <fstream>

namespace FxOgreMaxExporter
{

// The full path to the log file.
std::string FxOgreMaxExporterLogFile::_logPath;

// Sets the full path to the log file.
void FxOgreMaxExporterLogFile::SetPath( const std::string& logPath )
{
	_logPath = logPath;
	// Erase the contents of the log file.
	std::ofstream output(_logPath.c_str());
	FxOgreMaxExporterLog("Logging to file %s\n", _logPath.c_str());
}

// Returns the full path to the log file.
std::string FxOgreMaxExporterLogFile::GetPath( void )
{
	return _logPath;
}

// Printf-style log output.
void FxOgreMaxExporterLogFile::Log( const char* format, ... )
{
	va_list	argList;
	char buffer[1024];

	va_start(argList, format);
	vsprintf_s(buffer, 1024, format, argList);
	va_end(argList);

	if( _logPath.size() > 0 )
	{
		std::ofstream output(_logPath.c_str(), std::ios_base::app);
		if( output )
		{
			output << buffer ;//<< "\r\n";
		}
	}
}

void FxOgreMaxExporterLogFile::operator<<(const char* str)
{
	Log(str);
}


} // namespace


