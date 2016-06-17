////////////////////////////////////////////////////////////////////////////////
// FxOgreMaxExporterMaxScript.cpp
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


#include "FxOgreMaxExporterMaxScript.h"
#ifdef PRE_MAX_2011
#include "maxscrpt/maxscrpt.h"
#else
#include "maxscript/maxscript.h"
#endif


// =============================
// Begin Preprocessor nastiness
// =============================
// The use of Macros here is nasty, but helpful for reducing massively duplicate code.
// Maxscript only lets a single function have up to 11 parameters, so we need to have
// individual function access for getting and setting all booleans and strings in 
// the static paramaters found in FxOgreMaxExporterData.
#define BOOLEAN_VALUES exportMesh, \
	exportMaterial, \
	exportAnimCurves, \
	exportCameras, \
	exportAll, \
	exportVBA, \
	exportVertNorm, \
	exportVertCol, \
	exportTexCoord, \
	exportCamerasAnim, \
	exportSkeleton, \
	exportSkelAnims, \
	exportBSAnims, \
	exportVertAnims, \
	exportBlendShapes, \
	exportWorldCoords, \
	useSharedGeom, \
	lightingOff, \
	copyTextures, \
	exportParticles, \
	tangentsSplitMirrored, \
	tangentsSplitRotated, \
	tangentsUseParity, \
	buildTangents, \
	buildEdges, \
	skelBB, \
	bsBB, \
	vertBB, \
	normalizeScale, \
	yUpAxis, \
	exportScene,

#define RUN_MACRO_ON_ALL_BOOLEANS( MACRO_FUNCTION, BOOLEAN_VALUES ) \
	MACRO_FUNCTION( exportMesh ) \
	MACRO_FUNCTION( exportMaterial ) \
	MACRO_FUNCTION( exportAnimCurves ) \
	MACRO_FUNCTION( exportCameras ) \
	MACRO_FUNCTION( exportAll ) \
	MACRO_FUNCTION( exportVBA ) \
	MACRO_FUNCTION( exportVertNorm ) \
	MACRO_FUNCTION( exportVertCol ) \
	MACRO_FUNCTION( exportTexCoord ) \
	MACRO_FUNCTION( exportCamerasAnim ) \
	MACRO_FUNCTION( exportSkeleton ) \
	MACRO_FUNCTION( exportSkelAnims ) \
	MACRO_FUNCTION( exportBSAnims ) \
	MACRO_FUNCTION( exportVertAnims ) \
	MACRO_FUNCTION( exportBlendShapes ) \
	MACRO_FUNCTION( exportWorldCoords ) \
	MACRO_FUNCTION( useSharedGeom ) \
	MACRO_FUNCTION( lightingOff ) \
	MACRO_FUNCTION( copyTextures ) \
	MACRO_FUNCTION( exportParticles ) \
	MACRO_FUNCTION( tangentsSplitMirrored ) \
	MACRO_FUNCTION( tangentsSplitRotated ) \
	MACRO_FUNCTION( tangentsUseParity ) \
	MACRO_FUNCTION( buildTangents ) \
	MACRO_FUNCTION( buildEdges ) \
	MACRO_FUNCTION( skelBB ) \
	MACRO_FUNCTION( bsBB ) \
	MACRO_FUNCTION( vertBB ) \
	MACRO_FUNCTION( normalizeScale ) \
	MACRO_FUNCTION( yUpAxis ) \
	MACRO_FUNCTION( exportScene ) 
#define MAKE_FUNCTION_ENUM( var ) fn_get_##var, fn_set_##var,
#define STRINGIZE( var ) #var

#define MAKE_BOOLEAN_FUNCTION_MAP( boolVar ) \
	VFN_1 (fn_set_##boolVar, set_##boolVar, TYPE_STRING ); \
	FN_0 (fn_get_##boolVar, TYPE_BOOL, get_##boolVar );
#define MAKE_BOOLEAN_FUNCTION_DECLARATIONS( boolVar ) \
	virtual void set_##boolVar( TSTR value) = 0; \
	virtual bool get_##boolVar( ) = 0; 
#define	MAKE_BOOLEAN_FUNCTIONS( boolVar ) \
	void set_##boolVar(TSTR value) \
	{		\
		FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##boolVar = FX_OGRE_MAX_STRICMP(value.data(), FX_OGRE_MAX_T("on")) == 0;  \
	} \
	bool get_##boolVar( ) \
	{ \
		return FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##boolVar; \
	}
#define	MAKE_BOOLEAN_MIXININTERFACE( boolVar ) \
	fn_set_##boolVar, _T( STRINGIZE(set_##boolVar) ), 0, TYPE_VOID, 0, 1, _T(#boolVar), NULL, TYPE_STRING, \
	fn_get_##boolVar, _T( STRINGIZE(get_##boolVar) ), 0, TYPE_BOOL, 0, 0,

#define STRING_VALUES meshFilename, \
	skeletonFilename, \
	materialFilename, \
	animFilename, \
	camerasFilename, \
	particlesFilename, \
	matPrefix, \
	texOutputDir, \
	sceneFilename,
#define RUN_MACRO_ON_ALL_STRINGS( MACRO_FUNCTION, STRING_VALUES ) \
	MACRO_FUNCTION( meshFilename ) \
	MACRO_FUNCTION( skeletonFilename ) \
	MACRO_FUNCTION( materialFilename ) \
	MACRO_FUNCTION( animFilename ) \
	MACRO_FUNCTION( camerasFilename ) \
	MACRO_FUNCTION( particlesFilename ) \
	MACRO_FUNCTION( matPrefix ) \
	MACRO_FUNCTION( texOutputDir ) \
	MACRO_FUNCTION( sceneFilename )
#define MAKE_STRING_FUNCTION_MAP( stringVar ) \
	VFN_1 (fn_set_##stringVar, set_##stringVar, TYPE_STRING ); \
	FN_0 (fn_get_##stringVar, TYPE_TSTR, get_##stringVar );
#define MAKE_STRING_FUNCTION_DECLARATIONS( stringVar ) \
	virtual void set_##stringVar( TSTR value) = 0; \
	virtual TSTR* get_##stringVar( ) = 0; 
#define	MAKE_STRING_FUNCTIONS( stringVar ) \
	void set_##stringVar(TSTR value) \
	{		\
		FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##stringVar = FxOgreMaxExporter::string_tools::string_cast<FxOgreMaxExporter::ogre_string_type>(value.data());  \
	} \
	TSTR* get_##stringVar( ) \
	{ \
		TSTR* returnValue = new TSTR; \
		*returnValue = FxOgreMaxExporter::string_tools::string_cast<FxOgreMaxExporter::max_string_type>(FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##stringVar).c_str(); \
		return returnValue; \
	}
#define	MAKE_STRING_MIXININTERFACE( stringVar ) \
	fn_set_##stringVar, _T( STRINGIZE(set_##stringVar) ), 0, TYPE_VOID, 0, 1, _T(#stringVar), NULL, TYPE_STRING, \
	fn_get_##stringVar, _T( STRINGIZE(get_##stringVar) ), 0, TYPE_STRING, 0, 0,

#define CLIPLIST_VALUES skelClipList, BSClipList, vertClipList,
#define RUN_MACRO_ON_ALL_CLIPLISTS( MACRO_FUNCTION, CLIPLIST_VALUES ) \
	MACRO_FUNCTION( skelClipList ) \
	MACRO_FUNCTION( BSClipList ) \
	MACRO_FUNCTION( vertClipList )

#define MAKE_CLIPLIST_FUNCTION_MAP( cliplistVar ) \
	VFN_4 (fn_add_##cliplistVar, add_##cliplistVar, TYPE_STRING, TYPE_FLOAT, TYPE_FLOAT, TYPE_FLOAT ); \
	FN_1 (fn_remove_##cliplistVar, TYPE_BOOL, remove_##cliplistVar, TYPE_INT ); \
	FN_1 (fn_get_start_##cliplistVar, TYPE_FLOAT, get_start_##cliplistVar, TYPE_INT ); \
	FN_1 (fn_get_stop_##cliplistVar, TYPE_FLOAT, get_stop_##cliplistVar, TYPE_INT ); \
	FN_1 (fn_get_rate_##cliplistVar, TYPE_FLOAT, get_rate_##cliplistVar, TYPE_INT ); \
	FN_0 (fn_get_numClips_##cliplistVar, TYPE_INT, get_numClips_##cliplistVar ); \
	FN_1 (fn_get_name_##cliplistVar, TYPE_TSTR, get_name_##cliplistVar, TYPE_INT ); 

#define MAKE_CLIPLIST_FUNCTION_DECLARATIONS( cliplistVar ) \
	virtual void add_##cliplistVar( TSTR name, float start, float stop, float rate ) = 0; \
	virtual bool remove_##cliplistVar( int index ) = 0; \
	virtual float get_start_##cliplistVar( int index ) = 0; \
	virtual float get_stop_##cliplistVar( int index ) = 0; \
	virtual float get_rate_##cliplistVar( int index ) = 0; \
	virtual TSTR* get_name_##cliplistVar( int index ) = 0; \
	virtual int get_numClips_##cliplistVar( ) = 0; 

#define	MAKE_CLIPLIST_FUNCTIONS( cliplistVar ) \
	void add_##cliplistVar( TSTR name, float start, float stop, float rate )\
	{		\
		FxOgreMaxExporter::clipInfo clip; \
		clip.name = FxOgreMaxExporter::string_tools::string_cast<FxOgreMaxExporter::ogre_string_type>(name.data()); \
		clip.rate = rate; \
		clip.start = start; \
		clip.stop = stop; \
		for(int i = 0; i < FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.size(); ++i)\
		{\
			if(clip.name == FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar[i].name)\
				FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.erase(FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.begin()+i);\
		}\
		FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.push_back(clip);  \
	} \
	bool remove_##cliplistVar( int index )\
	{ \
		if(index >= 0 && index < FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.size()) \
		{ \
			FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.erase(FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.begin()+index);\
			return true; \
		} \
		return false; \
	} \
	float get_start_##cliplistVar( int index )\
	{\
		if(index >= 0 && index < FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.size()) \
		{ \
			return FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar[index].start;\
		}\
		return 0.0f;\
	}\
	float get_stop_##cliplistVar( int index )\
	{\
		if(index >= 0 && index < FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.size()) \
		{ \
			return FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar[index].stop;\
		}\
		return 0.0f;\
	}\
	float get_rate_##cliplistVar( int index )\
	{\
		if(index >= 0 && index < FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.size()) \
		{ \
			return FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar[index].rate;\
		}\
		return 0.0f;\
	}\
	TSTR* get_name_##cliplistVar( int index )\
	{\
		TSTR* returnValue = new TSTR;\
		if(index >= 0 && index < FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.size()) \
		{ \
			*returnValue = FxOgreMaxExporter::string_tools::string_cast<FxOgreMaxExporter::max_string_type>(FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar[index].name).c_str();\
		}\
		return returnValue;\
	}\
	int get_numClips_##cliplistVar()\
	{\
		return FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.##cliplistVar.size();\
	}

#define	MAKE_CLIPLIST_MIXININTERFACE( cliplistVar ) \
	fn_add_##cliplistVar, _T( STRINGIZE(add_##cliplistVar) ), 0, TYPE_VOID, 0, 4, _T("name"), NULL, TYPE_STRING, _T("start"), NULL, TYPE_FLOAT, _T("stop"), NULL, TYPE_FLOAT, _T("rate"), NULL, TYPE_FLOAT, \
	fn_remove_##cliplistVar, _T( STRINGIZE(remove_##cliplistVar) ), 0, TYPE_BOOL, 0, 1, _T("index"), NULL, TYPE_INT,\
	fn_get_start_##cliplistVar, _T( STRINGIZE(get_start_##cliplistVar) ), 0, TYPE_FLOAT, 0, 1, _T("index"), NULL, TYPE_INT,\
	fn_get_stop_##cliplistVar, _T( STRINGIZE(get_stop_##cliplistVar) ), 0, TYPE_FLOAT, 0, 1, _T("index"), NULL, TYPE_INT,\
	fn_get_rate_##cliplistVar, _T( STRINGIZE(get_rate_##cliplistVar) ), 0, TYPE_FLOAT, 0, 1, _T("index"), NULL, TYPE_INT,\
	fn_get_numClips_##cliplistVar, _T( STRINGIZE(get_numClips_##cliplistVar) ), 0, TYPE_INT, 0, 0,\
	fn_get_name_##cliplistVar, _T( STRINGIZE(get_name_##cliplistVar) ), 0, TYPE_TSTR, 0, 1, _T("index"), NULL, TYPE_INT,

#define MAKE_CLIPLIST_FUNCTION_ENUM( var ) fn_add_##var, fn_remove_##var, fn_get_start_##var, fn_get_stop_##var, fn_get_rate_##var, fn_get_numClips_##var, fn_get_name_##var,
// =============================
// End Preprocessor nastiness
// =============================


#define FXOGRE_INTERFACE_CLASS_ID Class_ID(0x8960f8ba, 0x60b5f8d0)
#define FXOGRE_MAXSCRIPT_INTERFACE Interface_ID(0x8ff94f28, 0x6216f0de)
#define GetFxOgreMaxScriptInterface(obj) ((FxOgreMaxScriptInterface*)obj->GetInterface(FXOGRE_MAXSCRIPT_INTERFACE))

static FxOgreMaxScriptInterfaceClassDesc fxOgreMaxScriptInterfaceClassDesc;

extern FPInterfaceDesc FxOgreMaxScript_mixininterface;

// Returns the class description for the FxOgre plug-in function publishing.
ClassDesc2* GetFxOgreMaxScriptInterfaceClassDesc( void )
{
	return &fxOgreMaxScriptInterfaceClassDesc;
}
enum {	
		fn_fxogremaxexport,
		fn_get_lum, fn_set_lum,
		fn_reset_params, 
		RUN_MACRO_ON_ALL_BOOLEANS( 	MAKE_FUNCTION_ENUM, BOOLEAN_VALUES )
		RUN_MACRO_ON_ALL_STRINGS( 	MAKE_FUNCTION_ENUM, STRING_VALUES )
		RUN_MACRO_ON_ALL_CLIPLISTS( MAKE_CLIPLIST_FUNCTION_ENUM, CLIPLIST_VALUES)
}; 
interface IFxMaxScript : public FPMixinInterface
{
	BEGIN_FUNCTION_MAP 
		VFN_0 (fn_fxogremaxexport, fxogremaxexport );
		VFN_1 (fn_set_lum, set_lum, TYPE_FLOAT );
		FN_0 (fn_get_lum, TYPE_FLOAT, get_lum );
		VFN_0 (fn_reset_params, reset_params );
		RUN_MACRO_ON_ALL_BOOLEANS( 	MAKE_BOOLEAN_FUNCTION_MAP, BOOLEAN_VALUES )
		RUN_MACRO_ON_ALL_STRINGS( 	MAKE_STRING_FUNCTION_MAP, STRING_VALUES )
		RUN_MACRO_ON_ALL_CLIPLISTS( MAKE_CLIPLIST_FUNCTION_MAP, CLIPLIST_VALUES )
    END_FUNCTION_MAP 

    FPInterfaceDesc* GetDesc() { return &FxOgreMaxScript_mixininterface; }
	virtual void		fxogremaxexport() = 0;
	virtual void		set_lum( float value ) = 0;
	virtual float		get_lum( ) = 0;
	virtual void		reset_params( ) = 0;
	RUN_MACRO_ON_ALL_BOOLEANS( 	MAKE_BOOLEAN_FUNCTION_DECLARATIONS, BOOLEAN_VALUES )	
	RUN_MACRO_ON_ALL_STRINGS( 	MAKE_STRING_FUNCTION_DECLARATIONS, STRING_VALUES )	
	RUN_MACRO_ON_ALL_CLIPLISTS( MAKE_CLIPLIST_FUNCTION_DECLARATIONS, CLIPLIST_VALUES )	
};


class FxOgre : public ReferenceTarget, public IFxMaxScript
{
	public:
		FxOgre(){ }
		void DeleteThis(){ delete this; }
		Class_ID ClassID(){ return FXOGRE_INTERFACE_CLASS_ID; }
		SClass_ID SuperClassID(){ return REF_TARGET_CLASS_ID; }
		void GetClassName(TSTR& s){ s = FX_OGRE_MAX_T("FxOgre"); }
		int IsKeyable(){ return 0;}
		RefResult NotifyRefChanged( Interval i, RefTargetHandle rth, PartID& pi,RefMessage rm )
		{
			return REF_SUCCEED;
		}
		BaseInterface* GetInterface(Interface_ID id) 
		{ 
			if (id == FXOGRE_MAXSCRIPT_INTERFACE) 
				return (IFxMaxScript*)this; 
			else 
				return ReferenceTarget::GetInterface(id); 
		}
		void fxogremaxexport() 
		{
			FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.exportScene();
		}
		void set_lum(float value) 
		{
			FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.lum = value;
		}
		float get_lum() 
		{
			return FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params.lum;
		}
		void reset_params() 
		{
			FxOgreMaxExporter::ParamList defaultParams;
			FxOgreMaxExporter::FxOgreMaxExporterData::maxInterface.m_params = defaultParams;
		}
		RUN_MACRO_ON_ALL_BOOLEANS( 	MAKE_BOOLEAN_FUNCTIONS, BOOLEAN_VALUES )
		RUN_MACRO_ON_ALL_STRINGS( 	MAKE_STRING_FUNCTIONS, STRING_VALUES )
		RUN_MACRO_ON_ALL_CLIPLISTS( MAKE_CLIPLIST_FUNCTIONS, CLIPLISTVALUES )
};

static FPInterfaceDesc FxOgreMaxScript_mixininterface(

    FXOGRE_MAXSCRIPT_INTERFACE, _T("FxOgre_Maxscript"), 0, &fxOgreMaxScriptInterfaceClassDesc, FP_MIXIN, 
	fn_fxogremaxexport, _T("fxogremaxexport"), 0, TYPE_VOID, 0, 0,
	fn_set_lum, _T("set_lum"), 0, TYPE_VOID, 0, 1, _T("lum"), NULL, TYPE_FLOAT,
	fn_get_lum, _T("get_lum"), 0, TYPE_FLOAT, 0, 0,
	fn_reset_params, _T("reset_params"), 0, TYPE_VOID, 0, 0,
	RUN_MACRO_ON_ALL_BOOLEANS( 	MAKE_BOOLEAN_MIXININTERFACE, BOOLEAN_VALUES )
	RUN_MACRO_ON_ALL_STRINGS( 	MAKE_STRING_MIXININTERFACE, STRING_VALUES )
	RUN_MACRO_ON_ALL_CLIPLISTS( MAKE_CLIPLIST_MIXININTERFACE, CLIPLIST_VALUES )
    // jcr 2012/6/11 Versions of max before 2013 use end, 2013 and later use
    // p_end. If MAX_RELEASE_R15 is defined (the define for 2013) then we're
    // sure we're using 2013 or later.
#if defined(MAX_RELEASE_R15)
    p_end
#else
    end
#endif // defined(MAX_RELEASE_R15)
);
// Controls if the plug-in shows up in lists from the user to choose from.
int FxOgreMaxScriptInterfaceClassDesc::IsPublic( void ) 
{ 
	return TRUE; 
}

// Max calls this method when it needs a pointer to a new instance of the 
// plug-in class.
void* FxOgreMaxScriptInterfaceClassDesc::Create( BOOL loading )
{ 
	return new FxOgre();
}

// Returns the name of the class.
const TCHAR* FxOgreMaxScriptInterfaceClassDesc::ClassName( void ) 
{ 
	return FX_OGRE_MAX_T("FxOgre");
}

// Returns a system defined constant describing the class this plug-in 
// class was derived from.
SClass_ID FxOgreMaxScriptInterfaceClassDesc::SuperClassID( void ) 
{ 
	return REF_TARGET_CLASS_ID; 
}

// Returns the unique ID for the object.
Class_ID FxOgreMaxScriptInterfaceClassDesc::ClassID( void ) 
{
	return FXOGRE_INTERFACE_CLASS_ID; 
}

// Returns a string describing the category the plug-in fits into.
const TCHAR* FxOgreMaxScriptInterfaceClassDesc::Category( void ) 
{ 
	return _T("");
}

// Returns a string which provides a fixed, machine parsable internal name 
// for the plug-in.  This name is used by MAXScript.
const TCHAR* FxOgreMaxScriptInterfaceClassDesc::InternalName( void ) 
{ 
	return _T("FxOgre"); 
}

// Returns the DLL instance handle of the plug-in.
HINSTANCE FxOgreMaxScriptInterfaceClassDesc::HInstance( void ) 
{ 
	return hInstance;
}
