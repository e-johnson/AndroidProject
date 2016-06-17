////////////////////////////////////////////////////////////////////////////////
// ogreExporter.h
// Author     : Francesco Giordana
// Start Date : January 13, 2005
// Copyright  : (C) 2006 by Francesco Giordana
// Email      : fra.giordana@tiscali.it
////////////////////////////////////////////////////////////////////////////////

/*********************************************************************************
*                                                                                *
*   This program is free software; you can redistribute it and/or modify         *
*   it under the terms of the GNU Lesser General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or            *
*   (at your option) any later version.                                          *
*                                                                                *
**********************************************************************************/
/*********************************************************************************
 * Description: This is a plugin for Maya, that allows the export of animated    *
 *              meshes in the OGRE file format. All meshes will be combined      *
 *              together to form a single OGRE mesh, each Maya mesh will be      *
 *              translated as a submesh. Multiple materials per mesh are allowed *
 *              each group of triangles sharing the same material will become    *
 *              a separate submesh. Skeletal animation and blendshapes are       *
 *              supported, or, alternatively, vertex animation as a sequence     *
 *              of morph targets.                                                *
 *              The export command can be run via script too, for instructions   *
 *              on its usage please refer to the Instructions.txt file.          *
 *********************************************************************************/
/*********************************************************************************
 * Note: The particles exporter is an extra module submitted by the OGRE         *
 *       community, it still has to be reviewed and fixed.                       *
 *********************************************************************************/
// Modified original version = Change Maya registration to allow co-existence with
// unmodified version.
// Author	  : Doug Perkowski - OC3 Entertainment, Inc.
// Start Date : December 10th, 2007
////////////////////////////////////////////////////////////////////////////////
#ifndef OGRE_EXPORTER_H
#define OGRE_EXPORTER_H

#include "mesh.h"
#include "scene.h"
#include "particles.h"
#include "mayaExportLayer.h"
#include <maya/MPxCommand.h>
#include <maya/MFnPlugin.h>
#include <maya/MFnLight.h>
#include <maya/MPxFileTranslator.h>
namespace OgreMayaExporter
{
	class FxOgreFileMenuExporter : public MPxFileTranslator
	{
	public:

		FxOgreFileMenuExporter();
		~FxOgreFileMenuExporter();
		MStatus reader( const MFileObject& file, const MString& optionsString,FileAccessMode mode);
		MStatus writer( const MFileObject& file, const MString& optionsString,FileAccessMode mode );
		bool haveReadMethod( void ) const;
		bool haveWriteMethod( void ) const;
		MString defaultExtension( void ) const;
		virtual MString	filter( void ) const;
		MFileKind identifyFile(	const MFileObject& fileName, const char* buffer,short size ) const;
		static void* creator( void );
	};

	class OgreExporter : public MPxCommand
	{
	public:
		// Public methods
		//constructor
		OgreExporter();
		//destructor
		virtual ~OgreExporter();
		//override of MPxCommand methods
		static void* creator();
		MStatus doIt(const MArgList& args);

		MStatus exportWithParams(ParamList &params);
		
		bool isUndoable() const;

	protected:
		// Internal methods
		//analyses a dag node in Maya and translates it to the OGRE format, 
		//it is recursively applied until the whole dag nodes tree has been visited
		MStatus translateNode(MDagPath& dagPath);
		//writes animation data to an extra .anim file
		MStatus writeAnim(MFnAnimCurve& anim);
		//writes camera data to an extra .camera file
		MStatus writeCamera(MFnCamera& camera);
		//writes all translated data to a group of OGRE files
		MStatus writeOgreData();
		//cleans up memory and exits
		void exit();
		// Doug Perkowski - Adding .Scene support
		// Return a filled out FxOgreNode from an MFnDagNode for writing to .scene file.
		FxOgreNode getFxOgreNode( MFnDagNode& dagNode );
		// Add camera to .scene file.
		MStatus addCameraToScene(MFnCamera& camera);
		// Add light to .scene file.
		MStatus addLightToScene(MFnLight& light);
		// Returns if the node is visible.
		bool _isVisible( const MFnDagNode& dagNode );
	private:
		// private members
		MStatus stat;
		ParamList m_params;
		Mesh* m_pMesh;
		MaterialSet* m_pMaterialSet;
		MSelectionList m_selList;
		MTime m_curTime;
		FxOgreScene m_FxOgreScene;
	};




	/*********************************************************************************************
	*                                  INLINE Functions                                         *
	*********************************************************************************************/
	// Standard constructor
	inline OgreExporter::OgreExporter()
		:m_pMesh(0), m_pMaterialSet(0)
	{
		MGlobal::displayInfo("Translating scene to OGRE format");
	}

	// Routine for creating the plug-in
	inline void* OgreExporter::creator()
	{
		return new OgreExporter();
	}

	// It tells that this command is not undoable
	inline bool OgreExporter::isUndoable() const
	{
		MGlobal::displayInfo("Command is not undoable");
		return false;
	}

}	//end namespace
#endif
