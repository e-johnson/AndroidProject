////////////////////////////////////////////////////////////////////////////////
// ogreExporter.cpp
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

#include "OgreExporter.h"
#include <maya/MFnNonAmbientLight.h>
#include <maya/MFnSpotLight.h>

namespace OgreMayaExporter
{
    OgreExporter::~OgreExporter()
    {
        exit();
    }
    // Restore the scene to a state previous to the export, clean up memory and exit
    void OgreExporter::exit()
    {
        // Restore active selection list
        MGlobal::setActiveSelectionList(m_selList);
        // Restore current time
        MAnimControl::setCurrentTime(m_curTime);
        // Free memory
        delete m_pMesh;
        m_pMesh = 0;
        delete m_pMaterialSet;
        m_pMaterialSet = 0;
        // Close output files
        m_params.closeFiles();
        std::cout.flush();
    }

    // Execute the command
    MStatus OgreExporter::doIt(const MArgList& args)
    {
        // Parse the arguments.
        ParamList params;
        params.parseArgs(args);

        return exportWithParams(params);
    }

    MStatus OgreExporter::exportWithParams(ParamList &params)
    {
        // clean up
        delete m_pMesh;
        delete m_pMaterialSet;

        m_params = params;
        // Create output files
        m_params.openFiles();
        // Create a new empty mesh
        m_pMesh = new Mesh();
        // Create a new empty material set
        m_pMaterialSet = new MaterialSet();
        // Save current time for later restore
        m_curTime = MAnimControl::currentTime();
        // Save active selection list for later restore
        MGlobal::getActiveSelectionList(m_selList);
        /**************************** LOAD DATA **********************************/

        if (m_params.exportAll)
        {	// We are exporting the whole scene
            std::cout << "Export the whole scene\n";
            std::cout.flush();
            MItDag dagIter;
            MFnDagNode worldDag (dagIter.root());
            MDagPath worldPath;
            worldDag.getPath(worldPath);
            stat = translateNode(worldPath);
        }
        else
        {	// We are translating a selection
            std::cout << "Export selected objects\n";
            std::cout.flush();
            // Get the selection list
            MSelectionList activeList;
            stat = MGlobal::getActiveSelectionList(activeList);
            if (MS::kSuccess != stat)
            {
                std::cout << "Error retrieving selection list\n";
                std::cout.flush();
                exit();
                return MS::kFailure;
            }
            MItSelectionList iter(activeList);

            for ( ; !iter.isDone(); iter.next())
            {								
                MDagPath dagPath;
                stat = iter.getDagPath(dagPath);
                stat = translateNode(dagPath); 
            }							
        }

        // Load skeleton animation (do it now, so we have loaded all needed joints)
        if (m_pMesh->getSkeleton() && m_params.exportSkelAnims)
        {
            // Restore skeleton to correct pose
            m_pMesh->getSkeleton()->restorePose();
            // Load skeleton animations
            m_pMesh->getSkeleton()->loadAnims(m_params);
        }

        // Load vertex animations
        if (m_params.exportVertAnims)
            m_pMesh->loadAnims(m_params);

        // Load blend shapes
        if (m_params.exportBlendShapes)
            m_pMesh->loadBlendShapes(m_params);

        // We export exactly one mesh at the origin in the .Scene file.
        // Exporting somewhere other than the origin could be useful when there is
        // 1) no skeleton and 2) m_params.exportWorldCoords is false (local space)
        // but even in this case, if there are multiple submeshes, I'm not sure which 
        // transform to use in the scene.  Exporting more than one mesh doesn't make 
        // sense because the exporter is designed to export one .MESH file at a time.
        if(m_params.exportScene && m_params.exportMesh)
        {
            FxOgreMesh meshNode;
            meshNode.node.trans.scale = FxOgrePoint3(1.0f, 1.0f, 1.0f);
            meshNode.node.trans.rot = FxOgrePoint4(1.0f, 0.0f, 0.0f, 0.0f);
            std::string filename = StripToTopParent(m_params.meshFilename.asChar());
            meshNode.meshFile = filename.c_str();
            int ri = filename.find_last_of(".");
            meshNode.node.name = filename.substr(0,filename.length()-5);
            m_FxOgreScene.addMesh(meshNode);
        }


        /**************************** WRITE DATA **********************************/
        stat = writeOgreData();

        std::cout << "Export completed succesfully\n";
        std::cout.flush();
        exit();

        return MS::kSuccess;
    }


    /**************************** TRANSLATE A NODE **********************************/
    // Method for iterating over nodes in a dependency graph from top to bottom
    MStatus OgreExporter::translateNode(MDagPath& dagPath)
    {
        MObject dagPathNode = dagPath.node();
        if( _isVisible(dagPathNode) )
        {
            if (m_params.exportAnimCurves )
            {
                MItDependencyGraph animIter( dagPathNode,
                    MFn::kAnimCurve,
                    MItDependencyGraph::kUpstream,
                    MItDependencyGraph::kDepthFirst,
                    MItDependencyGraph::kNodeLevel,
                    &stat );

                if (stat)
                {
                    for (; !animIter.isDone(); animIter.next())
                    {
                        MObject anim = animIter.thisNode(&stat);
                        MFnAnimCurve animFn(anim,&stat);
                        std::cout << "Found animation curve: " << animFn.name().asChar() << "\n";
                        std::cout << "Translating animation curve: " << animFn.name().asChar() << "...\n";
                        std::cout.flush();
                        stat = writeAnim(animFn);
                        if (MS::kSuccess == stat)
                        {
                            std::cout << "OK\n";
                            std::cout.flush();
                        }
                        else
                        {
                            std::cout << "Error, Aborting operation\n";
                            std::cout.flush();
                            return MS::kFailure;
                        }
                    }
                }
            }
            if (dagPath.hasFn(MFn::kMesh)&&(m_params.exportMesh||m_params.exportMaterial||m_params.exportSkeleton)
                && (dagPath.childCount() == 0))
            {	// we have found a mesh shape node, it can't have any children, and it contains
                // all the mesh geometry data
                MDagPath meshDag = dagPath;
                MFnMesh meshFn(meshDag);
                if (!meshFn.isIntermediateObject())
                {
                    std::cout << "Found mesh node: " << meshDag.fullPathName().asChar() << "\n";
                    std::cout << "Loading mesh node " << meshDag.fullPathName().asChar() << "...\n";
                    std::cout.flush();
                    stat = m_pMesh->load(meshDag,m_params);
                    if (MS::kSuccess == stat)
                    {
                        std::cout << "OK\n";
                        std::cout.flush();
                    }
                    else
                    {
                        std::cout << "Error, mesh skipped\n";
                        std::cout.flush();
                    }
                }
            }
            else if (dagPath.hasFn(MFn::kCamera)&&(m_params.exportCameras ) && (!dagPath.hasFn(MFn::kShape)))
            {	// we have found a camera shape node, it can't have any children, and it contains
                // all information about the camera
                MFnCamera cameraFn(dagPath);
                if (!cameraFn.isIntermediateObject())
                {
                    std::cout <<  "Found camera node: "<< dagPath.fullPathName().asChar() << "\n";

                    if(m_params.exportCameras)
                    {
                        std::cout <<  "Translating camera node: "<< dagPath.fullPathName().asChar() << "...\n";
                        std::cout.flush();
                        stat = writeCamera(cameraFn);
                        if (MS::kSuccess == stat)
                        {
                            std::cout << "OK\n";
                            std::cout.flush();
                        }
                        else
                        {
                            std::cout << "Error, Aborting operation\n";
                            std::cout.flush();
                            return MS::kFailure;
                        }
                    }
                }
            }
            else if ( ( dagPath.apiType() == MFn::kParticle ) && m_params.exportParticles )
            {	// we have found a set of particles
                MFnDagNode fnNode(dagPath);
                if (!fnNode.isIntermediateObject())
                {
                    std::cout <<  "Found particles node: "<< dagPath.fullPathName().asChar() << "\n";
                    std::cout <<  "Translating particles node: "<< dagPath.fullPathName().asChar() << "...\n";
                    std::cout.flush();
                    Particles particles;
                    particles.load(dagPath,m_params);
                    stat = particles.writeToXML(m_params);
                    if (MS::kSuccess == stat)
                    {
                        std::cout << "OK\n";
                        std::cout.flush();
                    }
                    else
                    {
                        std::cout << "Error, Aborting operation\n";
                        std::cout.flush();
                        return MS::kFailure;
                    }
                }
            }
            if(m_params.exportScene)
            {
                std::string nodeType = dagPath.node().apiTypeStr();
                std::string pLightType = "kPointLight";
                std::string dLightType = "kDirectionalLight";
                std::string sLightType = "kSpotLight";
                std::string cameraType = "kCamera";

                if( nodeType == cameraType )
                {
                    MFnCamera cameraFn(dagPath);
                    std::cout <<  "Adding camera node to scene: "<< dagPath.fullPathName().asChar() << "...\n";
                    addCameraToScene(cameraFn);	
                }
                else if(	pLightType		==  nodeType || 
                            dLightType		==  nodeType ||
                            sLightType		==  nodeType		)
                {
                    MFnLight lightFn(dagPath);
                    if (!lightFn.isIntermediateObject())
                    {
                        std::cout <<  "Found light node: "<< dagPath.fullPathName().asChar() << "\n";
                        std::cout <<  "Adding light node to scene: "<< dagPath.fullPathName().asChar() << "...\n";
                        addLightToScene(lightFn);
                    }
                }
            }
        
            // look for meshes and cameras within the node's children
            for (unsigned int i=0; i<dagPath.childCount(); i++)
            {
                MObject child = dagPath.child(i);
                 MDagPath childPath = dagPath;
                stat = childPath.push(child);
                if (MS::kSuccess != stat)
                {
                    std::cout << "Error retrieving path to child " << i << " of: " << dagPath.fullPathName().asChar();
                    std::cout.flush();
                    return MS::kFailure;
                }
                stat = translateNode(childPath);
                if (MS::kSuccess != stat)
                    return MS::kFailure;
            }
        }
        return MS::kSuccess;
    }



    /********************************************************************************************************
    *                       Method to translate a single animation curve                                   *
    ********************************************************************************************************/
    MStatus OgreExporter::writeAnim(MFnAnimCurve& anim)
    {
        m_params.outAnim << "anim " << anim.name().asChar() << "\n";
        m_params.outAnim <<"{\n";
        m_params.outAnim << "\t//Time   /    Value\n";

        for (unsigned int i=0; i<anim.numKeys(); i++)
            m_params.outAnim << "\t" << anim.time(i).as(MTime::kSeconds) << "\t" << anim.value(i) << "\n";

        m_params.outAnim << "}\n\n";
        return MS::kSuccess;
    }

    FxOgreNode OgreExporter::getFxOgreNode( MFnDagNode& dagNode )
    {
        MStatus status;
        FxOgreNode node;
        node.name = dagNode.partialPathName().asChar();
        
        MDagPath path;
        status = dagNode.getPath(path);
        if(status == MS::kSuccess )
        {
            MObject transformObject = path.transform(&status);
            if(status == MS::kSuccess )
            {
                MFnTransform transform(transformObject);

                // Translation
                MVector translation = transform.transformation().translation(MSpace::kWorld);
                node.trans.pos.x = translation.x;
                node.trans.pos.y = translation.y;
                node.trans.pos.z = translation.z;

                // Rotation
                double qx,qy,qz,qw;
                transform.transformation().getRotationQuaternion(qx,qy,qz,qw, MSpace::kWorld);
                node.trans.rot.w = qw;
                node.trans.rot.x = qx;
                node.trans.rot.y = qy;
                node.trans.rot.z = qz;

                // Scale
                double scale[3];
                transform.transformation().getScale(scale,MSpace::kWorld);
                node.trans.scale.x = scale[0];
                node.trans.scale.y = scale[1];
                node.trans.scale.z = scale[2];
            }
        }
        return node;
    }

    // Doug Perkowski - 03/31/2008 - Adding a camera export to a .scene file.
    MStatus OgreExporter::addCameraToScene(MFnCamera& mfn_camera)
    {
        FxOgreCamera camera;
        camera.node = getFxOgreNode(mfn_camera);
        // TODO: Not sure what to do with vertical field of view. 
        camera.fov = (float)mfn_camera.horizontalFieldOfView();
        camera.clipNear = (float)mfn_camera.nearClippingPlane();
        camera.clipFar= (float)mfn_camera.farClippingPlane();
        m_FxOgreScene.addCamera(camera);
        return MS::kSuccess;
    }
    MStatus OgreExporter::addLightToScene(MFnLight& mfn_light)
    {
        FxOgreLight light;
        light.node = getFxOgreNode(mfn_light);
        MColor col = mfn_light.color();
        light.diffuseColour = FxOgrePoint3(col.r, col.g, col.b);

        col = mfn_light.lightIntensity();
        light.specularColour = FxOgrePoint3(col.r, col.g, col.b);

        MDagPath dagPath = mfn_light.dagPath();
        std::string pLightType = "kPointLight";
        std::string dLightType = "kDirectionalLight";
        std::string sLightType = "kSpotLight";
        std::string nodeType = dagPath.node().apiTypeStr();

        if( nodeType == pLightType)
        {
            light.type = OGRE_LIGHT_POINT;
        }
        else if( nodeType == dLightType )
        {
            light.type = OGRE_LIGHT_DIRECTIONAL;
        }
        else if( nodeType == sLightType)
        {
            light.type = OGRE_LIGHT_SPOT;
        }
        else
        {
            std::cout << "Unsupported light type:" << dagPath.fullPathName().asChar() << "\n";
            return MS::kFailure;
        }
        // TODO: how do I detect a OGRE_LIGHT_RADPOINT?
        if( dagPath.hasFn(MFn::kNonAmbientLight))
        {
            MFnNonAmbientLight nonAmbientLightFn(dagPath);
            // A decay of 0 is no decay, 1 is linear, 2 is square, 3 is max.
            short decay = nonAmbientLightFn.decayRate();
            short intensity = mfn_light.intensity();
            // Todo: Fix this so that it works correctly.  
            if(decay < 1.0f)
            {
                light.attenuation_constant = decay;
            }
            else if(decay < 2.0f)
            {
                light.attenuation_linear = decay;
            }
            else
            {
                light.attenuation_quadratic = decay;
            }
            light.attenuation_range = 0.0f;
        }
        if( dagPath.hasFn(MFn::kSpotLight))
        {
            MFnSpotLight spotLight(dagPath);
            light.range_inner = spotLight.penumbraAngle();
            light.range_outer = spotLight.coneAngle();
            light.range_falloff = spotLight.dropOff();
        }
        m_FxOgreScene.addLight(light);
        return MS::kSuccess;
    }

    /********************************************************************************************************
    *                           Method to translate a single camera                                        *
    ********************************************************************************************************/
    MStatus OgreExporter::writeCamera(MFnCamera& camera)
    {
        int i;
        MPlug plug;
        MPlugArray srcplugarray;
        double dist;
        MAngle angle;
        MFnTransform* cameraTransform = NULL;
        MFnAnimCurve* animCurve = NULL;
        // get camera transform
        for (i=0; i<camera.parentCount(); i++)
        {
            if (camera.parent(i).hasFn(MFn::kTransform))
            {
                cameraTransform = new MFnTransform(camera.parent(i));
                continue;
            }
        }
        // start camera description
        m_params.outCameras << "camera " << cameraTransform->partialPathName().asChar() << "\n";
        m_params.outCameras << "{\n";

        //write camera type
        m_params.outCameras << "\ttype ";
        if (camera.isOrtho())
            m_params.outCameras << "ortho\n";
        else
            m_params.outCameras << "persp\n";

        // write translation data
        m_params.outCameras << "\ttranslation\n";
        m_params.outCameras << "\t{\n";
        //translateX
        m_params.outCameras << "\t\tx ";
        plug = cameraTransform->findPlug("translateX");
        if (plug.isConnected() && m_params.exportCamerasAnim)
        {
            plug.connectedTo(srcplugarray,true,false,&stat);
            for (i=0; i < srcplugarray.length(); i++)
            {
                if (srcplugarray[i].node().hasFn(MFn::kAnimCurve))
                {
                    if (animCurve)
                        delete animCurve;
                    animCurve = new MFnAnimCurve(srcplugarray[i].node());
                    continue;
                }
                else if (i == srcplugarray.length()-1)
                {
                    std::cout << "Invalid link to translateX attribute\n";
                    return MS::kFailure;
                }
            }
            m_params.outCameras << "anim " << animCurve->name().asChar() << "\n";
        }
        else
        {
            plug.getValue(dist);
            m_params.outCameras << "= " << dist << "\n";
        }
        //translateY
        m_params.outCameras << "\t\ty ";
        plug = cameraTransform->findPlug("translateY");
        if (plug.isConnected() && m_params.exportCamerasAnim)
        {
            plug.connectedTo(srcplugarray,true,false,&stat);
            for (i=0; i< srcplugarray.length(); i++)
            {
                if (srcplugarray[i].node().hasFn(MFn::kAnimCurve))
                {
                    if (animCurve)
                        delete animCurve;
                    animCurve = new MFnAnimCurve(srcplugarray[i].node());
                    continue;
                }
                else if (i == srcplugarray.length()-1)
                {
                    std::cout << "Invalid link to translateY attribute\n";
                    return MS::kFailure;
                }
            }
            m_params.outCameras << "anim " << animCurve->name().asChar() << "\n";
        }
        else
        {
            plug.getValue(dist);
            m_params.outCameras << "= " << dist << "\n";
        }
        //translateZ
        m_params.outCameras << "\t\tz ";
        plug = cameraTransform->findPlug("translateZ");
        if (plug.isConnected() && m_params.exportCamerasAnim)
        {
            plug.connectedTo(srcplugarray,true,false,&stat);
            for (i=0; i< srcplugarray.length(); i++)
            {
                if (srcplugarray[i].node().hasFn(MFn::kAnimCurve))
                {
                    if (animCurve)
                        delete animCurve;
                    animCurve = new MFnAnimCurve(srcplugarray[i].node());
                    continue;
                }
                else if (i == srcplugarray.length()-1)
                {
                    std::cout << "Invalid link to translateZ attribute\n";
                    return MS::kFailure;
                }
            }
            m_params.outCameras << "anim " << animCurve->name().asChar() << "\n";
        }
        else
        {
            plug.getValue(dist);
            m_params.outCameras << "= " << dist << "\n";
        }
        m_params.outCameras << "\t}\n";

        // write rotation data
        m_params.outCameras << "\trotation\n";
        m_params.outCameras << "\t{\n";
        m_params.outCameras << "\t\tx ";
        //rotateX
        plug = cameraTransform->findPlug("rotateX");
        if (plug.isConnected() && m_params.exportCamerasAnim)
        {
            plug.connectedTo(srcplugarray,true,false,&stat);
            for (i=0; i< srcplugarray.length(); i++)
            {
                if (srcplugarray[i].node().hasFn(MFn::kAnimCurve))
                {
                    if (animCurve)
                        delete animCurve;
                    animCurve = new MFnAnimCurve(srcplugarray[i].node());
                    continue;
                }
                else if (i == srcplugarray.length()-1)
                {
                    std::cout << "Invalid link to rotateX attribute\n";
                    return MS::kFailure;
                }
            }
            m_params.outCameras << "anim " << animCurve->name().asChar() << "\n";
        }
        else
        {
            plug.getValue(angle);
            m_params.outCameras << "= " << angle.asDegrees() << "\n";
        }
        //rotateY
        m_params.outCameras << "\t\ty ";
        plug = cameraTransform->findPlug("rotateY");
        if (plug.isConnected() && m_params.exportCamerasAnim)
        {
            plug.connectedTo(srcplugarray,true,false,&stat);
            for (i=0; i< srcplugarray.length(); i++)
            {
                if (srcplugarray[i].node().hasFn(MFn::kAnimCurve))
                {
                    if (animCurve)
                        delete animCurve;
                    animCurve = new MFnAnimCurve(srcplugarray[i].node());
                    continue;
                }
                else if (i == srcplugarray.length()-1)
                {
                    std::cout << "Invalid link to rotateY attribute\n";
                    return MS::kFailure;
                }
            }
            m_params.outCameras << "anim " << animCurve->name().asChar() << "\n";
        }
        else
        {
            plug.getValue(angle);
            m_params.outCameras << "= " << angle.asDegrees() << "\n";
        }
        //rotateZ
        m_params.outCameras << "\t\tz ";
        plug = cameraTransform->findPlug("rotateZ");
        if (plug.isConnected() && m_params.exportCamerasAnim)
        {
            plug.connectedTo(srcplugarray,true,false,&stat);
            for (i=0; i< srcplugarray.length(); i++)
            {
                if (srcplugarray[i].node().hasFn(MFn::kAnimCurve))
                {
                    if (animCurve)
                        delete animCurve;
                    animCurve = new MFnAnimCurve(srcplugarray[i].node());
                    continue;
                }
                else if (i == srcplugarray.length()-1)
                {
                    std::cout << "Invalid link to rotateZ attribute\n";
                    return MS::kFailure;
                }
            }
            m_params.outCameras << "anim " << animCurve->name().asChar() << "\n";
        }
        else
        {
            plug.getValue(angle);
            m_params.outCameras << "= " << angle.asDegrees() << "\n";
        }
        m_params.outCameras << "\t}\n";

        // end camera description
        m_params.outCameras << "}\n\n";
        if (cameraTransform != NULL)
            delete cameraTransform;
        if (animCurve != NULL)
            delete animCurve;
        return MS::kSuccess;
    }

    /********************************************************************************************************
    *                           Method to write data to OGRE format                                         *
    ********************************************************************************************************/
    MStatus OgreExporter::writeOgreData()
    {
        // Create Ogre Root
//		Ogre::Root ogreRoot;
        // Create singletons
        Ogre::LogManager logMgr;

        // Doug Perkowski - 02/04/09
        // Creating default log to avoid crashes in skeleton serialization.
        Ogre::LogManager::getSingleton().createLog("Ogre.log", true);
        Ogre::ResourceGroupManager rgm;
        Ogre::MeshManager meshMgr;
        Ogre::SkeletonManager skelMgr;
        Ogre::MaterialManager matMgr;
        Ogre::DefaultHardwareBufferManager hardwareBufMgr;
        
        // Doug Perkowski  - 03/09/10
        // Creating LodStrategyManager
        // http://www.ogre3d.org/forums/viewtopic.php?f=8&t=55844
        Ogre::LodStrategyManager lodstrategymanager;   
        
        // Write mesh binary
        if (m_params.exportMesh)
        {
            std::cout << "Writing mesh binary...\n";
            std::cout.flush();
            stat = m_pMesh->writeOgreBinary(m_params);
            if (stat != MS::kSuccess)
            {
                std::cout << "Error writing mesh binary file\n";
                std::cout.flush();
            }
        }

        // Write skeleton binary
        if (m_params.exportSkeleton)
        {
            if (m_pMesh->getSkeleton())
            {
                std::cout << "Writing skeleton binary...\n";
                std::cout.flush();
                stat = m_pMesh->getSkeleton()->writeOgreBinary(m_params);
                if (stat != MS::kSuccess)
                {
                    std::cout << "Error writing skeleton binary file\n";
                    std::cout.flush();
                }
            }
            else
            {
                std::cout << "Could not export a skeleton because no joints were found.  Make sure the mesh is weighted to bones.\n";
                MGlobal::executeCommand("confirmDialog 	-title \"Error\" -message \"Failure: No joints were found. Make sure the mesh is weighted to bones.  No .skeleton file will be exported.\"", true);
            }
        }
        
        // Write materials data
        if (m_params.exportMaterial)
        {
            std::cout << "Writing materials data...\n";
            std::cout.flush();
            stat  = m_pMaterialSet->writeOgreScript(m_params);
            if (stat != MS::kSuccess)
            {
                std::cout << "Error writing materials file\n";
                std::cout.flush();
            }
        }
        // Write Scene
        if (m_params.exportScene)
        {
            std::cout << "Writing scene data...\n";
            std::cout.flush();
            stat  = m_FxOgreScene.writeSceneFile(m_params);
            if (stat != MS::kSuccess)
            {
                std::cout << "Error writing scene file\n";
                std::cout.flush();
            }
        }
        m_FxOgreScene.clear();
        return MS::kSuccess;
    }

    // Routine for registering the command within Maya
    MStatus initializePlugin( MObject obj )
    {
        MStatus   status;
        MFnPlugin plugin( obj, "FxOgreExporter", "7.0", "Any");
        status = plugin.registerCommand( "FxOgreExport", OgreExporter::creator );
        if (!status) {
            status.perror("registerCommand");
            return status;
        }
        // Doug Perkowski - Adding support for exporting via the File menu.
        // Register the translator with the system.
        status =  plugin.registerFileTranslator("FxOgre Files", "none",
            FxOgreFileMenuExporter::creator, 
            "",	 // Options script.
            ""); // Default options.

        if( MS::kSuccess != status ) 
        {
            status.perror("registerFileTranslator");
        }

        return status;
    }

    // Routine for unregistering the command within Maya
    MStatus uninitializePlugin( MObject obj)
    {
        MStatus   status;
        MFnPlugin plugin( obj );
        status = plugin.deregisterCommand( "FxOgreExport" );
        if (!status) {
            status.perror("deregisterCommand");
            return status;
        }
        // Doug Perkowski - Adding support for exporting via the File menu.
        status =  plugin.deregisterFileTranslator("FxOgre Files");
        if( MS::kSuccess != status ) 
        {
            status.perror("deregisterFileTranslator");
        }
        return status;
    }



    // Doug Perkowski - Adding support for exporting via the File menu.
    FxOgreFileMenuExporter::FxOgreFileMenuExporter()
    {
    }
    FxOgreFileMenuExporter::~FxOgreFileMenuExporter()
    {
    }
    MStatus	FxOgreFileMenuExporter::reader( const MFileObject& file, const MString& options, FileAccessMode mode )
    {
        std::cerr << "FxOgreFileMenuExporter::reader() method unimplimented!\n" << std::endl;
        return MS::kFailure;
    }

    MStatus	FxOgreFileMenuExporter::writer( const MFileObject& file, const MString& options, FileAccessMode mode )
    {
        ParamList params;
        OgreExporter exporter;

        // Using only a mesh filename, construct the other filenames according to the
        // default behavior: Skeleton and material filenames match mesh, and material prefix
        // matching the mesh filename.
        std::string temp, meshFilename, skeletonFilename, materialFilename, matPrefix, filenamePath,  sceneFilename;
        temp = meshFilename = file.fullName().asChar();
        for (int i=0; i<temp.length(); ++i)
        {
            temp[i]=toupper(temp[i]);
        } 
        size_t meshIndex = temp.rfind(".MESH", temp.length() -1);
        size_t folderIndexForward = temp.rfind("/", temp.length() -1);
        size_t folderIndexBackward = temp.rfind("\\", temp.length() -1);
        size_t folderIndex;
        if(folderIndexForward == std::string::npos)
        {
            folderIndex = folderIndexBackward;
        }
        else if(folderIndexBackward == std::string::npos)
        {
            folderIndex = folderIndexForward;
        }
        else
        {
            folderIndex = folderIndexBackward > folderIndexForward ? folderIndexBackward : folderIndexForward;
        }
        if(meshIndex == std::string::npos || folderIndex == std::string::npos)
        {
            std::cout << "Invalid mesh filename: " << meshFilename.c_str() << "\n";
            return MS::kFailure;
        }
        skeletonFilename = meshFilename.substr(0,meshIndex).append(".SKELETON");
        materialFilename = meshFilename.substr(0,meshIndex).append(".MATERIAL");
        sceneFilename = meshFilename.substr(0,meshIndex).append(".SCENE");
        
        matPrefix = meshFilename.substr(folderIndex, temp.length() -1);
        filenamePath =  meshFilename.substr(0, folderIndex);

        // Setup default paramlist suitable for exporting most talking character setups.
        params.exportMesh = true;
        params.exportMaterial = true;
        params.exportSkeleton = true;
        params.exportSkelAnims = false;
        params.exportBSAnims = false;
        params.exportVertAnims = false;
        params.exportBlendShapes = true;
        params.exportAnimCurves = false;
        params.exportCameras = false;
        params.exportParticles = false;
        params.exportAll = true;
        params.exportWorldCoords = true;
        params.exportVBA = true;
        params.exportVertNorm = true;
        params.exportVertCol = false;
        params.exportTexCoord = true;
        params.exportCamerasAnim = false;
        params.useSharedGeom = true;
        params.lightingOff = false;
        params.copyTextures = true;
        params.skelBB = false;
        params.bsBB = false;
        params.vertBB = false;
        params.meshFilename = meshFilename.c_str();
        params.skeletonFilename = skeletonFilename.c_str();
        params.materialFilename = materialFilename.c_str();
        params.animFilename = "";
        params.camerasFilename = "";
        params.particlesFilename = "";
        params.matPrefix = matPrefix.c_str();
        params.texOutputDir = filenamePath.c_str();
        params.skelClipList.clear();
        params.BSClipList.clear();
        params.vertClipList.clear();
        params.neutralPoseType = NPT_CURFRAME;
        params.buildEdges = false;
        params.buildTangents = false;
        params.tangentsSplitMirrored = false;
        params.tangentsSplitRotated = false;
        params.tangentsUseParity = false;
        params.tangentSemantic = TS_TANGENT;
        params.loadedSubmeshes.clear();
        params.currentRootJoints.clear();
        params.exportScene = true;
        params.sceneFilename = sceneFilename.c_str();
        params.useBlendshapeDeformerName = true;
        if( MPxFileTranslator::kExportActiveAccessMode == mode )
        {
            params.exportAll = false;
        }
        if(	!exporter.exportWithParams(params) )
        {
            return MS::kFailure;
        }
        return MS::kSuccess;
    }

    bool FxOgreFileMenuExporter::haveReadMethod( void ) const 
    {
        return false;
    }

    bool FxOgreFileMenuExporter::haveWriteMethod( void ) const 
    {
        return true;
    }

    MString FxOgreFileMenuExporter::defaultExtension( void ) const 
    {
        return MString("MESH");
    }

    MString FxOgreFileMenuExporter::filter( void ) const
    {
        return MString("*.MESH");
    }

    MPxFileTranslator::MFileKind FxOgreFileMenuExporter::identifyFile( const MFileObject& fileName, const char* buffer, short size ) const 
    {
        const char* str = fileName.name().asChar();
        unsigned int len = fileName.name().length();
        if( str[len-4] == 'm' &&
            str[len-3] == 'e' &&
            str[len-2] == 's' &&
            str[len-1] == 'h')
        {
            return kCouldBeMyFileType;
        }
        return kNotMyFileType;
    }

    void* FxOgreFileMenuExporter::creator( void ) 
    {
        return new FxOgreFileMenuExporter;
    }
    bool OgreExporter::_isVisible( const MFnDagNode& dagNode )
    {
        bool isVisible = false;
        if( dagNode.isIntermediateObject() )
        {
            return false;
        }
        else
        {
            MStatus status;
            MPlug visibilityPlug = dagNode.findPlug("visibility", &status);
            if( !status )
            {
                std::cout << "No visibility attribute for node " << dagNode.name().asChar() << ", assuming not visible!\n";
                return false;
            }
            else
            {
                status = visibilityPlug.getValue(isVisible);
                if( !status )
                {
                    std::cout << "Can't query visibility attribute for node " << dagNode.name().asChar() << ", assuming not visible!\n";
                    return false;
                }
            }
        }
        return isVisible;
    }
} // end namespace
