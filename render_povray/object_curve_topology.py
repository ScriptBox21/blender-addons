# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# #**** END GPL LICENSE BLOCK #****

# <pep8 compliant>

"""Translate to POV the control point compounded geometries like polygon

meshes or curve based shapes.
"""

import bpy

from .shading import write_object_material

################################ LOFT, ETC.
def export_curves(ob, string_strip_hyphen, global_matrix, tab_write):
    """write all curves based POV primitives to exported file """
    name_orig = "OB" + ob.name
    dataname_orig = "DATA" + ob.data.name

    name = string_strip_hyphen(bpy.path.clean_name(name_orig))
    dataname = string_strip_hyphen(bpy.path.clean_name(dataname_orig))

    matrix = global_matrix @ ob.matrix_world
    bezier_sweep = False
    if ob.pov.curveshape == 'sphere_sweep':
        # inlined spheresweep macro, which itself calls Shapes.inc:
        file.write('        #include "shapes.inc"\n')

        file.write(
            '        #macro Shape_Bezierpoints_Sphere_Sweep(_merge_shape, _resolution, _points_array, _radius_array)\n'
        )
        file.write('        //input adjusting and inspection\n')
        file.write('        #if(_resolution <= 1)\n')
        file.write('            #local res = 1;\n')
        file.write('        #else\n')
        file.write('            #local res = int(_resolution);\n')
        file.write('        #end\n')
        file.write('        #if(dimensions(_points_array) != 1 | dimensions(_radius_array) != 1)\n')
        file.write('            #error ""\n')
        file.write(
            '        #elseif(div(dimension_size(_points_array,1),4) - dimension_size(_points_array,1)/4 != 0)\n'
        )
        file.write('            #error ""\n')
        file.write(
            '        #elseif(dimension_size(_points_array,1) != dimension_size(_radius_array,1))\n'
        )
        file.write('            #error ""\n')
        file.write('        #else\n')
        file.write('            #local n_of_seg = div(dimension_size(_points_array,1), 4);\n')
        file.write('            #local ctrl_pts_array = array[n_of_seg]\n')
        file.write('            #local ctrl_rs_array = array[n_of_seg]\n')
        file.write('            #for(i, 0, n_of_seg-1)\n')
        file.write(
            '                #local ctrl_pts_array[i] = array[4] {_points_array[4*i], _points_array[4*i+1], _points_array[4*i+2], _points_array[4*i+3]}\n'
        )
        file.write(
            '                #local ctrl_rs_array[i] = array[4] {abs(_radius_array[4*i]), abs(_radius_array[4*i+1]), abs(_radius_array[4*i+2]), abs(_radius_array[4*i+3])}\n'
        )
        file.write('            #end\n')
        file.write('        #end\n')

        file.write('        //drawing\n')
        file.write('        #local mockup1 =\n')
        file.write('        #if(_merge_shape) merge{ #else union{ #end\n')
        file.write('            #for(i, 0, n_of_seg-1)\n')
        file.write('                #local has_head = true;\n')
        file.write('                #if(i = 0)\n')
        file.write(
            '                    #if(vlength(ctrl_pts_array[i][0]-ctrl_pts_array[n_of_seg-1][3]) = 0 & ctrl_rs_array[i][0]-ctrl_rs_array[n_of_seg-1][3] <= 0)\n'
        )
        file.write('                        #local has_head = false;\n')
        file.write('                    #end\n')
        file.write('                #else\n')
        file.write(
            '                    #if(vlength(ctrl_pts_array[i][0]-ctrl_pts_array[i-1][3]) = 0 & ctrl_rs_array[i][0]-ctrl_rs_array[i-1][3] <= 0)\n'
        )
        file.write('                        #local has_head = false;\n')
        file.write('                    #end\n')
        file.write('                #end\n')
        file.write('                #if(has_head = true)\n')
        file.write('                    sphere{\n')
        file.write('                    ctrl_pts_array[i][0], ctrl_rs_array[i][0]\n')
        file.write('                    }\n')
        file.write('                #end\n')
        file.write('                #local para_t = (1/2)/res;\n')
        file.write(
            '                #local this_point = ctrl_pts_array[i][0]*pow(1-para_t,3) + ctrl_pts_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_pts_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_pts_array[i][3]*pow(para_t,3);\n'
        )
        file.write(
            '                #local this_radius = ctrl_rs_array[i][0]*pow(1-para_t,3) + ctrl_rs_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_rs_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_rs_array[i][3]*pow(para_t,3);\n'
        )
        file.write(
            '                #if(vlength(this_point-ctrl_pts_array[i][0]) > abs(this_radius-ctrl_rs_array[i][0]))\n'
        )
        file.write('                    object{\n')
        file.write(
            '                    Connect_Spheres(ctrl_pts_array[i][0], ctrl_rs_array[i][0], this_point, this_radius)\n'
        )
        file.write('                    }\n')
        file.write('                #end\n')
        file.write('                sphere{\n')
        file.write('                this_point, this_radius\n')
        file.write('                }\n')
        file.write('                #for(j, 1, res-1)\n')
        file.write('                    #local last_point = this_point;\n')
        file.write('                    #local last_radius = this_radius;\n')
        file.write('                    #local para_t = (1/2+j)/res;\n')
        file.write(
            '                    #local this_point = ctrl_pts_array[i][0]*pow(1-para_t,3) + ctrl_pts_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_pts_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_pts_array[i][3]*pow(para_t,3);\n'
        )
        file.write(
            '                    #local this_radius = ctrl_rs_array[i][0]*pow(1-para_t,3) + ctrl_rs_array[i][1]*3*pow(1-para_t,2)*para_t + ctrl_rs_array[i][2]*3*(1-para_t)*pow(para_t,2) + ctrl_rs_array[i][3]*pow(para_t,3);\n'
        )
        file.write(
            '                    #if(vlength(this_point-last_point) > abs(this_radius-last_radius))\n'
        )
        file.write('                        object{\n')
        file.write(
            '                        Connect_Spheres(last_point, last_radius, this_point, this_radius)\n'
        )
        file.write('                        }\n')
        file.write('                    #end\n')
        file.write('                    sphere{\n')
        file.write('                    this_point, this_radius\n')
        file.write('                    }\n')
        file.write('                #end\n')
        file.write('                #local last_point = this_point;\n')
        file.write('                #local last_radius = this_radius;\n')
        file.write('                #local this_point = ctrl_pts_array[i][3];\n')
        file.write('                #local this_radius = ctrl_rs_array[i][3];\n')
        file.write(
            '                #if(vlength(this_point-last_point) > abs(this_radius-last_radius))\n'
        )
        file.write('                    object{\n')
        file.write(
            '                    Connect_Spheres(last_point, last_radius, this_point, this_radius)\n'
        )
        file.write('                    }\n')
        file.write('                #end\n')
        file.write('                sphere{\n')
        file.write('                this_point, this_radius\n')
        file.write('                }\n')
        file.write('            #end\n')
        file.write('        }\n')
        file.write('        mockup1\n')
        file.write('        #end\n')

        for spl in ob.data.splines:
            if spl.type == "BEZIER":
                bezier_sweep = True
    if ob.pov.curveshape in {'loft', 'birail'}:
        n = 0
        for spline in ob.data.splines:
            n += 1
            tab_write('#declare %s%s=spline {\n' % (dataname, n))
            tab_write('cubic_spline\n')
            lp = len(spline.points)
            delta = 1 / (lp)
            d = -delta
            point = spline.points[lp - 1]
            x, y, z, w = point.co[:]
            tab_write('%.6f, <%.6f,%.6f,%.6f>\n' % (d, x, y, z))
            d += delta
            for point in spline.points:
                x, y, z, w = point.co[:]
                tab_write('%.6f, <%.6f,%.6f,%.6f>\n' % (d, x, y, z))
                d += delta
            for i in range(2):
                point = spline.points[i]
                x, y, z, w = point.co[:]
                tab_write('%.6f, <%.6f,%.6f,%.6f>\n' % (d, x, y, z))
                d += delta
            tab_write('}\n')
        if ob.pov.curveshape in {'loft'}:
            n = len(ob.data.splines)
            tab_write('#declare %s = array[%s]{\n' % (dataname, (n + 3)))
            tab_write('spline{%s%s},\n' % (dataname, n))
            for i in range(n):
                tab_write('spline{%s%s},\n' % (dataname, (i + 1)))
            tab_write('spline{%s1},\n' % (dataname))
            tab_write('spline{%s2}\n' % (dataname))
            tab_write('}\n')
        # Use some of the Meshmaker.inc macro, here inlined
        file.write('#macro CheckFileName(FileName)\n')
        file.write('   #local Len=strlen(FileName);\n')
        file.write('   #if(Len>0)\n')
        file.write('      #if(file_exists(FileName))\n')
        file.write('         #if(Len>=4)\n')
        file.write('            #local Ext=strlwr(substr(FileName,Len-3,4))\n')
        file.write(
            '            #if (strcmp(Ext,".obj")=0 | strcmp(Ext,".pcm")=0 | strcmp(Ext,".arr")=0)\n'
        )
        file.write('               #local Return=99;\n')
        file.write('            #else\n')
        file.write('               #local Return=0;\n')
        file.write('            #end\n')
        file.write('         #else\n')
        file.write('            #local Return=0;\n')
        file.write('         #end\n')
        file.write('      #else\n')
        file.write('         #if(Len>=4)\n')
        file.write('            #local Ext=strlwr(substr(FileName,Len-3,4))\n')
        file.write(
            '            #if (strcmp(Ext,".obj")=0 | strcmp(Ext,".pcm")=0 | strcmp(Ext,".arr")=0)\n'
        )
        file.write('               #if (strcmp(Ext,".obj")=0)\n')
        file.write('                  #local Return=2;\n')
        file.write('               #end\n')
        file.write('               #if (strcmp(Ext,".pcm")=0)\n')
        file.write('                  #local Return=3;\n')
        file.write('               #end\n')
        file.write('               #if (strcmp(Ext,".arr")=0)\n')
        file.write('                  #local Return=4;\n')
        file.write('               #end\n')
        file.write('            #else\n')
        file.write('               #local Return=1;\n')
        file.write('            #end\n')
        file.write('         #else\n')
        file.write('            #local Return=1;\n')
        file.write('         #end\n')
        file.write('      #end\n')
        file.write('   #else\n')
        file.write('      #local Return=1;\n')
        file.write('   #end\n')
        file.write('   (Return)\n')
        file.write('#end\n')

        file.write('#macro BuildSpline(Arr, SplType)\n')
        file.write('   #local Ds=dimension_size(Arr,1);\n')
        file.write('   #local Asc=asc(strupr(SplType));\n')
        file.write('   #if(Asc!=67 & Asc!=76 & Asc!=81) \n')
        file.write('      #local Asc=76;\n')
        file.write(
            '      #debug "\nWrong spline type defined (C/c/L/l/N/n/Q/q), using default linear_spline\\n"\n'
        )
        file.write('   #end\n')
        file.write('   spline {\n')
        file.write('      #switch (Asc)\n')
        file.write('         #case (67) //C  cubic_spline\n')
        file.write('            cubic_spline\n')
        file.write('         #break\n')
        file.write('         #case (76) //L  linear_spline\n')
        file.write('            linear_spline\n')
        file.write('         #break\n')
        file.write('         #case (78) //N  linear_spline\n')
        file.write('            natural_spline\n')
        file.write('         #break\n')
        file.write('         #case (81) //Q  Quadratic_spline\n')
        file.write('            quadratic_spline\n')
        file.write('         #break\n')
        file.write('      #end\n')
        file.write('      #local Add=1/((Ds-2)-1);\n')
        file.write('      #local J=0-Add;\n')
        file.write('      #local I=0;\n')
        file.write('      #while (I<Ds)\n')
        file.write('         J\n')
        file.write('         Arr[I]\n')
        file.write('         #local I=I+1;\n')
        file.write('         #local J=J+Add;\n')
        file.write('      #end\n')
        file.write('   }\n')
        file.write('#end\n')

        file.write('#macro BuildWriteMesh2(VecArr, NormArr, UVArr, U, V, FileName)\n')
        # suppressed some file checking from original macro because no more separate files
        file.write(' #local Write=0;\n')
        file.write(' #debug concat("\\n\\n Building mesh2: \\n   - vertex_vectors\\n")\n')
        file.write('  #local NumVertices=dimension_size(VecArr,1);\n')
        file.write('  #switch (Write)\n')
        file.write('     #case(1)\n')
        file.write('        #write(\n')
        file.write('           MeshFile,\n')
        file.write('           "  vertex_vectors {\\n",\n')
        file.write('           "    ", str(NumVertices,0,0),"\\n    "\n')
        file.write('        )\n')
        file.write('     #break\n')
        file.write('     #case(2)\n')
        file.write('        #write(\n')
        file.write('           MeshFile,\n')
        file.write('           "# Vertices: ",str(NumVertices,0,0),"\\n"\n')
        file.write('        )\n')
        file.write('     #break\n')
        file.write('     #case(3)\n')
        file.write('        #write(\n')
        file.write('           MeshFile,\n')
        file.write('           str(2*NumVertices,0,0),",\\n"\n')
        file.write('        )\n')
        file.write('     #break\n')
        file.write('     #case(4)\n')
        file.write('        #write(\n')
        file.write('           MeshFile,\n')
        file.write('           "#declare VertexVectors= array[",str(NumVertices,0,0),"] {\\n  "\n')
        file.write('        )\n')
        file.write('     #break\n')
        file.write('  #end\n')
        file.write('  mesh2 {\n')
        file.write('     vertex_vectors {\n')
        file.write('        NumVertices\n')
        file.write('        #local I=0;\n')
        file.write('        #while (I<NumVertices)\n')
        file.write('           VecArr[I]\n')
        file.write('           #switch(Write)\n')
        file.write('              #case(1)\n')
        file.write('                 #write(MeshFile, VecArr[I])\n')
        file.write('              #break\n')
        file.write('              #case(2)\n')
        file.write('                 #write(\n')
        file.write('                    MeshFile,\n')
        file.write(
            '                    "v ", VecArr[I].x," ", VecArr[I].y," ", VecArr[I].z,"\\n"\n'
        )
        file.write('                 )\n')
        file.write('              #break\n')
        file.write('              #case(3)\n')
        file.write('                 #write(\n')
        file.write('                    MeshFile,\n')
        file.write('                    VecArr[I].x,",", VecArr[I].y,",", VecArr[I].z,",\\n"\n')
        file.write('                 )\n')
        file.write('              #break\n')
        file.write('              #case(4)\n')
        file.write('                 #write(MeshFile, VecArr[I])\n')
        file.write('              #break\n')
        file.write('           #end\n')
        file.write('           #local I=I+1;\n')
        file.write('           #if(Write=1 | Write=4)\n')
        file.write('              #if(mod(I,3)=0)\n')
        file.write('                 #write(MeshFile,"\\n    ")\n')
        file.write('              #end\n')
        file.write('           #end \n')
        file.write('        #end\n')
        file.write('        #switch(Write)\n')
        file.write('           #case(1)\n')
        file.write('              #write(MeshFile,"\\n  }\\n")\n')
        file.write('           #break\n')
        file.write('           #case(2)\n')
        file.write('              #write(MeshFile,"\\n")\n')
        file.write('           #break\n')
        file.write('           #case(3)\n')
        file.write('              // do nothing\n')
        file.write('           #break\n')
        file.write('           #case(4) \n')
        file.write('              #write(MeshFile,"\\n}\\n")\n')
        file.write('           #break\n')
        file.write('        #end\n')
        file.write('     }\n')

        file.write('     #debug concat("   - normal_vectors\\n")    \n')
        file.write('     #local NumVertices=dimension_size(NormArr,1);\n')
        file.write('     #switch(Write)\n')
        file.write('        #case(1)\n')
        file.write('           #write(\n')
        file.write('              MeshFile,\n')
        file.write('              "  normal_vectors {\\n",\n')
        file.write('              "    ", str(NumVertices,0,0),"\\n    "\n')
        file.write('           )\n')
        file.write('        #break\n')
        file.write('        #case(2)\n')
        file.write('           #write(\n')
        file.write('              MeshFile,\n')
        file.write('              "# Normals: ",str(NumVertices,0,0),"\\n"\n')
        file.write('           )\n')
        file.write('        #break\n')
        file.write('        #case(3)\n')
        file.write('           // do nothing\n')
        file.write('        #break\n')
        file.write('        #case(4)\n')
        file.write('           #write(\n')
        file.write('              MeshFile,\n')
        file.write(
            '              "#declare NormalVectors= array[",str(NumVertices,0,0),"] {\\n  "\n'
        )
        file.write('           )\n')
        file.write('        #break\n')
        file.write('     #end\n')
        file.write('     normal_vectors {\n')
        file.write('        NumVertices\n')
        file.write('        #local I=0;\n')
        file.write('        #while (I<NumVertices)\n')
        file.write('           NormArr[I]\n')
        file.write('           #switch(Write)\n')
        file.write('              #case(1)\n')
        file.write('                 #write(MeshFile NormArr[I])\n')
        file.write('              #break\n')
        file.write('              #case(2)\n')
        file.write('                 #write(\n')
        file.write('                    MeshFile,\n')
        file.write(
            '                    "vn ", NormArr[I].x," ", NormArr[I].y," ", NormArr[I].z,"\\n"\n'
        )
        file.write('                 )\n')
        file.write('              #break\n')
        file.write('              #case(3)\n')
        file.write('                 #write(\n')
        file.write('                    MeshFile,\n')
        file.write('                    NormArr[I].x,",", NormArr[I].y,",", NormArr[I].z,",\\n"\n')
        file.write('                 )\n')
        file.write('              #break\n')
        file.write('              #case(4)\n')
        file.write('                 #write(MeshFile NormArr[I])\n')
        file.write('              #break\n')
        file.write('           #end\n')
        file.write('           #local I=I+1;\n')
        file.write('           #if(Write=1 | Write=4) \n')
        file.write('              #if(mod(I,3)=0)\n')
        file.write('                 #write(MeshFile,"\\n    ")\n')
        file.write('              #end\n')
        file.write('           #end\n')
        file.write('        #end\n')
        file.write('        #switch(Write)\n')
        file.write('           #case(1)\n')
        file.write('              #write(MeshFile,"\\n  }\\n")\n')
        file.write('           #break\n')
        file.write('           #case(2)\n')
        file.write('              #write(MeshFile,"\\n")\n')
        file.write('           #break\n')
        file.write('           #case(3)\n')
        file.write('              //do nothing\n')
        file.write('           #break\n')
        file.write('           #case(4)\n')
        file.write('              #write(MeshFile,"\\n}\\n")\n')
        file.write('           #break\n')
        file.write('        #end\n')
        file.write('     }\n')

        file.write('     #debug concat("   - uv_vectors\\n")   \n')
        file.write('     #local NumVertices=dimension_size(UVArr,1);\n')
        file.write('     #switch(Write)\n')
        file.write('        #case(1)\n')
        file.write('           #write(\n')
        file.write('              MeshFile, \n')
        file.write('              "  uv_vectors {\\n",\n')
        file.write('              "    ", str(NumVertices,0,0),"\\n    "\n')
        file.write('           )\n')
        file.write('         #break\n')
        file.write('         #case(2)\n')
        file.write('           #write(\n')
        file.write('              MeshFile,\n')
        file.write('              "# UV-vectors: ",str(NumVertices,0,0),"\\n"\n')
        file.write('           )\n')
        file.write('         #break\n')
        file.write('         #case(3)\n')
        file.write('           // do nothing, *.pcm does not support uv-vectors\n')
        file.write('         #break\n')
        file.write('         #case(4)\n')
        file.write('            #write(\n')
        file.write('               MeshFile,\n')
        file.write('               "#declare UVVectors= array[",str(NumVertices,0,0),"] {\\n  "\n')
        file.write('            )\n')
        file.write('         #break\n')
        file.write('     #end\n')
        file.write('     uv_vectors {\n')
        file.write('        NumVertices\n')
        file.write('        #local I=0;\n')
        file.write('        #while (I<NumVertices)\n')
        file.write('           UVArr[I]\n')
        file.write('           #switch(Write)\n')
        file.write('              #case(1)\n')
        file.write('                 #write(MeshFile UVArr[I])\n')
        file.write('              #break\n')
        file.write('              #case(2)\n')
        file.write('                 #write(\n')
        file.write('                    MeshFile,\n')
        file.write('                    "vt ", UVArr[I].u," ", UVArr[I].v,"\\n"\n')
        file.write('                 )\n')
        file.write('              #break\n')
        file.write('              #case(3)\n')
        file.write('                 //do nothing\n')
        file.write('              #break\n')
        file.write('              #case(4)\n')
        file.write('                 #write(MeshFile UVArr[I])\n')
        file.write('              #break\n')
        file.write('           #end\n')
        file.write('           #local I=I+1; \n')
        file.write('           #if(Write=1 | Write=4)\n')
        file.write('              #if(mod(I,3)=0)\n')
        file.write('                 #write(MeshFile,"\\n    ")\n')
        file.write('              #end \n')
        file.write('           #end\n')
        file.write('        #end \n')
        file.write('        #switch(Write)\n')
        file.write('           #case(1)\n')
        file.write('              #write(MeshFile,"\\n  }\\n")\n')
        file.write('           #break\n')
        file.write('           #case(2)\n')
        file.write('              #write(MeshFile,"\\n")\n')
        file.write('           #break\n')
        file.write('           #case(3)\n')
        file.write('              //do nothing\n')
        file.write('           #break\n')
        file.write('           #case(4)\n')
        file.write('              #write(MeshFile,"\\n}\\n")\n')
        file.write('           #break\n')
        file.write('        #end\n')
        file.write('     }\n')
        file.write('\n')
        file.write('     #debug concat("   - face_indices\\n")   \n')
        file.write('     #declare NumFaces=U*V*2;\n')
        file.write('     #switch(Write)\n')
        file.write('        #case(1)\n')
        file.write('           #write(\n')
        file.write('              MeshFile,\n')
        file.write('              "  face_indices {\\n"\n')
        file.write('              "    ", str(NumFaces,0,0),"\\n    "\n')
        file.write('           )\n')
        file.write('        #break\n')
        file.write('        #case(2)\n')
        file.write('           #write (\n')
        file.write('              MeshFile,\n')
        file.write('              "# faces: ",str(NumFaces,0,0),"\\n"\n')
        file.write('           )\n')
        file.write('        #break\n')
        file.write('        #case(3)\n')
        file.write('           #write (\n')
        file.write('              MeshFile,\n')
        file.write('              "0,",str(NumFaces,0,0),",\\n"\n')
        file.write('           )\n')
        file.write('        #break\n')
        file.write('        #case(4)\n')
        file.write('           #write(\n')
        file.write('              MeshFile,\n')
        file.write('              "#declare FaceIndices= array[",str(NumFaces,0,0),"] {\\n  "\n')
        file.write('           )\n')
        file.write('        #break\n')
        file.write('     #end\n')
        file.write('     face_indices {\n')
        file.write('        NumFaces\n')
        file.write('        #local I=0;\n')
        file.write('        #local H=0;\n')
        file.write('        #local NumVertices=dimension_size(VecArr,1);\n')
        file.write('        #while (I<V)\n')
        file.write('           #local J=0;\n')
        file.write('           #while (J<U)\n')
        file.write('              #local Ind=(I*U)+I+J;\n')
        file.write('              <Ind, Ind+1, Ind+U+2>, <Ind, Ind+U+1, Ind+U+2>\n')
        file.write('              #switch(Write)\n')
        file.write('                 #case(1)\n')
        file.write('                    #write(\n')
        file.write('                       MeshFile,\n')
        file.write('                       <Ind, Ind+1, Ind+U+2>, <Ind, Ind+U+1, Ind+U+2>\n')
        file.write('                    )\n')
        file.write('                 #break\n')
        file.write('                 #case(2)\n')
        file.write('                    #write(\n')
        file.write('                       MeshFile,\n')
        file.write(
            '                       "f ",Ind+1,"/",Ind+1,"/",Ind+1," ",Ind+1+1,"/",Ind+1+1,"/",Ind+1+1," ",Ind+U+2+1,"/",Ind+U+2+1,"/",Ind+U+2+1,"\\n",\n'
        )
        file.write(
            '                       "f ",Ind+U+1+1,"/",Ind+U+1+1,"/",Ind+U+1+1," ",Ind+1,"/",Ind+1,"/",Ind+1," ",Ind+U+2+1,"/",Ind+U+2+1,"/",Ind+U+2+1,"\\n"\n'
        )
        file.write('                    )\n')
        file.write('                 #break\n')
        file.write('                 #case(3)\n')
        file.write('                    #write(\n')
        file.write('                       MeshFile,\n')
        file.write(
            '                       Ind,",",Ind+NumVertices,",",Ind+1,",",Ind+1+NumVertices,",",Ind+U+2,",",Ind+U+2+NumVertices,",\\n"\n'
        )
        file.write(
            '                       Ind+U+1,",",Ind+U+1+NumVertices,",",Ind,",",Ind+NumVertices,",",Ind+U+2,",",Ind+U+2+NumVertices,",\\n"\n'
        )
        file.write('                    )\n')
        file.write('                 #break\n')
        file.write('                 #case(4)\n')
        file.write('                    #write(\n')
        file.write('                       MeshFile,\n')
        file.write('                       <Ind, Ind+1, Ind+U+2>, <Ind, Ind+U+1, Ind+U+2>\n')
        file.write('                    )\n')
        file.write('                 #break\n')
        file.write('              #end\n')
        file.write('              #local J=J+1;\n')
        file.write('              #local H=H+1;\n')
        file.write('              #if(Write=1 | Write=4)\n')
        file.write('                 #if(mod(H,3)=0)\n')
        file.write('                    #write(MeshFile,"\\n    ")\n')
        file.write('                 #end \n')
        file.write('              #end\n')
        file.write('           #end\n')
        file.write('           #local I=I+1;\n')
        file.write('        #end\n')
        file.write('     }\n')
        file.write('     #switch(Write)\n')
        file.write('        #case(1)\n')
        file.write('           #write(MeshFile, "\\n  }\\n}")\n')
        file.write('           #fclose MeshFile\n')
        file.write('           #debug concat(" Done writing\\n")\n')
        file.write('        #break\n')
        file.write('        #case(2)\n')
        file.write('           #fclose MeshFile\n')
        file.write('           #debug concat(" Done writing\\n")\n')
        file.write('        #break\n')
        file.write('        #case(3)\n')
        file.write('           #fclose MeshFile\n')
        file.write('           #debug concat(" Done writing\\n")\n')
        file.write('        #break\n')
        file.write('        #case(4)\n')
        file.write('           #write(MeshFile, "\\n}\\n}")\n')
        file.write('           #fclose MeshFile\n')
        file.write('           #debug concat(" Done writing\\n")\n')
        file.write('        #break\n')
        file.write('     #end\n')
        file.write('  }\n')
        file.write('#end\n')

        file.write('#macro MSM(SplineArray, SplRes, Interp_type,  InterpRes, FileName)\n')
        file.write('    #declare Build=CheckFileName(FileName);\n')
        file.write('    #if(Build=0)\n')
        file.write('        #debug concat("\\n Parsing mesh2 from file: ", FileName, "\\n")\n')
        file.write('        #include FileName\n')
        file.write('        object{Surface}\n')
        file.write('    #else\n')
        file.write('        #local NumVertices=(SplRes+1)*(InterpRes+1);\n')
        file.write('        #local NumFaces=SplRes*InterpRes*2;\n')
        file.write(
            '        #debug concat("\\n Calculating ",str(NumVertices,0,0)," vertices for ", str(NumFaces,0,0)," triangles\\n\\n")\n'
        )
        file.write('        #local VecArr=array[NumVertices]\n')
        file.write('        #local NormArr=array[NumVertices]\n')
        file.write('        #local UVArr=array[NumVertices]\n')
        file.write('        #local N=dimension_size(SplineArray,1);\n')
        file.write('        #local TempSplArr0=array[N];\n')
        file.write('        #local TempSplArr1=array[N];\n')
        file.write('        #local TempSplArr2=array[N];\n')
        file.write('        #local PosStep=1/SplRes;\n')
        file.write('        #local InterpStep=1/InterpRes;\n')
        file.write('        #local Count=0;\n')
        file.write('        #local Pos=0;\n')
        file.write('        #while(Pos<=1)\n')
        file.write('            #local I=0;\n')
        file.write('            #if (Pos=0)\n')
        file.write('                #while (I<N)\n')
        file.write('                    #local Spl=spline{SplineArray[I]}\n')
        file.write('                    #local TempSplArr0[I]=<0,0,0>+Spl(Pos);\n')
        file.write('                    #local TempSplArr1[I]=<0,0,0>+Spl(Pos+PosStep);\n')
        file.write('                    #local TempSplArr2[I]=<0,0,0>+Spl(Pos-PosStep);\n')
        file.write('                    #local I=I+1;\n')
        file.write('                #end\n')
        file.write('                #local S0=BuildSpline(TempSplArr0, Interp_type)\n')
        file.write('                #local S1=BuildSpline(TempSplArr1, Interp_type)\n')
        file.write('                #local S2=BuildSpline(TempSplArr2, Interp_type)\n')
        file.write('            #else\n')
        file.write('                #while (I<N)\n')
        file.write('                    #local Spl=spline{SplineArray[I]}\n')
        file.write('                    #local TempSplArr1[I]=<0,0,0>+Spl(Pos+PosStep);\n')
        file.write('                    #local I=I+1;\n')
        file.write('                #end\n')
        file.write('                #local S1=BuildSpline(TempSplArr1, Interp_type)\n')
        file.write('            #end\n')
        file.write('            #local J=0;\n')
        file.write('            #while (J<=1)\n')
        file.write('                #local P0=<0,0,0>+S0(J);\n')
        file.write('                #local P1=<0,0,0>+S1(J);\n')
        file.write('                #local P2=<0,0,0>+S2(J);\n')
        file.write('                #local P3=<0,0,0>+S0(J+InterpStep);\n')
        file.write('                #local P4=<0,0,0>+S0(J-InterpStep);\n')
        file.write('                #local B1=P4-P0;\n')
        file.write('                #local B2=P2-P0;\n')
        file.write('                #local B3=P3-P0;\n')
        file.write('                #local B4=P1-P0;\n')
        file.write('                #local N1=vcross(B1,B2);\n')
        file.write('                #local N2=vcross(B2,B3);\n')
        file.write('                #local N3=vcross(B3,B4);\n')
        file.write('                #local N4=vcross(B4,B1);\n')
        file.write('                #local Norm=vnormalize((N1+N2+N3+N4));\n')
        file.write('                #local VecArr[Count]=P0;\n')
        file.write('                #local NormArr[Count]=Norm;\n')
        file.write('                #local UVArr[Count]=<J,Pos>;\n')
        file.write('                #local J=J+InterpStep;\n')
        file.write('                #local Count=Count+1;\n')
        file.write('            #end\n')
        file.write('            #local S2=spline{S0}\n')
        file.write('            #local S0=spline{S1}\n')
        file.write(
            '            #debug concat("\\r Done ", str(Count,0,0)," vertices : ", str(100*Count/NumVertices,0,2)," %")\n'
        )
        file.write('            #local Pos=Pos+PosStep;\n')
        file.write('        #end\n')
        file.write('        BuildWriteMesh2(VecArr, NormArr, UVArr, InterpRes, SplRes, "")\n')
        file.write('    #end\n')
        file.write('#end\n\n')

        file.write('#macro Coons(Spl1, Spl2, Spl3, Spl4, Iter_U, Iter_V, FileName)\n')
        file.write('   #declare Build=CheckFileName(FileName);\n')
        file.write('   #if(Build=0)\n')
        file.write('      #debug concat("\\n Parsing mesh2 from file: ", FileName, "\\n")\n')
        file.write('      #include FileName\n')
        file.write('      object{Surface}\n')
        file.write('   #else\n')
        file.write('      #local NumVertices=(Iter_U+1)*(Iter_V+1);\n')
        file.write('      #local NumFaces=Iter_U*Iter_V*2;\n')
        file.write(
            '      #debug concat("\\n Calculating ", str(NumVertices,0,0), " vertices for ",str(NumFaces,0,0), " triangles\\n\\n")\n'
        )
        file.write('      #declare VecArr=array[NumVertices]   \n')
        file.write('      #declare NormArr=array[NumVertices]   \n')
        file.write('      #local UVArr=array[NumVertices]      \n')
        file.write('      #local Spl1_0=Spl1(0);\n')
        file.write('      #local Spl2_0=Spl2(0);\n')
        file.write('      #local Spl3_0=Spl3(0);\n')
        file.write('      #local Spl4_0=Spl4(0);\n')
        file.write('      #local UStep=1/Iter_U;\n')
        file.write('      #local VStep=1/Iter_V;\n')
        file.write('      #local Count=0;\n')
        file.write('      #local I=0;\n')
        file.write('      #while (I<=1)\n')
        file.write('         #local Im=1-I;\n')
        file.write('         #local J=0;\n')
        file.write('         #while (J<=1)\n')
        file.write('            #local Jm=1-J;\n')
        file.write(
            '            #local C0=Im*Jm*(Spl1_0)+Im*J*(Spl2_0)+I*J*(Spl3_0)+I*Jm*(Spl4_0);\n'
        )
        file.write('            #local P0=LInterpolate(I, Spl1(J), Spl3(Jm)) + \n')
        file.write('               LInterpolate(Jm, Spl2(I), Spl4(Im))-C0;\n')
        file.write('            #declare VecArr[Count]=P0;\n')
        file.write('            #local UVArr[Count]=<J,I>;\n')
        file.write('            #local J=J+UStep;\n')
        file.write('            #local Count=Count+1;\n')
        file.write('         #end\n')
        file.write('         #debug concat(\n')
        file.write('            "\r Done ", str(Count,0,0)," vertices :         ",\n')
        file.write('            str(100*Count/NumVertices,0,2)," %"\n')
        file.write('         )\n')
        file.write('         #local I=I+VStep;\n')
        file.write('      #end\n')
        file.write('      #debug "\r Normals                                  "\n')
        file.write('      #local Count=0;\n')
        file.write('      #local I=0;\n')
        file.write('      #while (I<=Iter_V)\n')
        file.write('         #local J=0;\n')
        file.write('         #while (J<=Iter_U)\n')
        file.write('            #local Ind=(I*Iter_U)+I+J;\n')
        file.write('            #local P0=VecArr[Ind];\n')
        file.write('            #if(J=0)\n')
        file.write('               #local P1=P0+(P0-VecArr[Ind+1]);\n')
        file.write('            #else\n')
        file.write('               #local P1=VecArr[Ind-1];\n')
        file.write('            #end\n')
        file.write('            #if (J=Iter_U)\n')
        file.write('               #local P2=P0+(P0-VecArr[Ind-1]);\n')
        file.write('            #else\n')
        file.write('               #local P2=VecArr[Ind+1];\n')
        file.write('            #end\n')
        file.write('            #if (I=0)\n')
        file.write('               #local P3=P0+(P0-VecArr[Ind+Iter_U+1]);\n')
        file.write('            #else\n')
        file.write('               #local P3=VecArr[Ind-Iter_U-1];\n')
        file.write('            #end\n')
        file.write('            #if (I=Iter_V)\n')
        file.write('               #local P4=P0+(P0-VecArr[Ind-Iter_U-1]);\n')
        file.write('            #else\n')
        file.write('               #local P4=VecArr[Ind+Iter_U+1];\n')
        file.write('            #end\n')
        file.write('            #local B1=P4-P0;\n')
        file.write('            #local B2=P2-P0;\n')
        file.write('            #local B3=P3-P0;\n')
        file.write('            #local B4=P1-P0;\n')
        file.write('            #local N1=vcross(B1,B2);\n')
        file.write('            #local N2=vcross(B2,B3);\n')
        file.write('            #local N3=vcross(B3,B4);\n')
        file.write('            #local N4=vcross(B4,B1);\n')
        file.write('            #local Norm=vnormalize((N1+N2+N3+N4));\n')
        file.write('            #declare NormArr[Count]=Norm;\n')
        file.write('            #local J=J+1;\n')
        file.write('            #local Count=Count+1;\n')
        file.write('         #end\n')
        file.write(
            '         #debug concat("\r Done ", str(Count,0,0)," normals : ",str(100*Count/NumVertices,0,2), " %")\n'
        )
        file.write('         #local I=I+1;\n')
        file.write('      #end\n')
        file.write('      BuildWriteMesh2(VecArr, NormArr, UVArr, Iter_U, Iter_V, FileName)\n')
        file.write('   #end\n')
        file.write('#end\n\n')
    # Empty curves
    if len(ob.data.splines) == 0:
        tab_write("\n//dummy sphere to represent empty curve location\n")
        tab_write("#declare %s =\n" % dataname)
        tab_write(
            "sphere {<%.6g, %.6g, %.6g>,0 pigment{rgbt 1} no_image no_reflection no_radiosity photons{pass_through collect off} hollow}\n\n"
            % (ob.location.x, ob.location.y, ob.location.z)
        )  # ob.name > povdataname)
    # And non empty curves
    else:
        if not bezier_sweep:
            tab_write("#declare %s =\n" % dataname)
        if ob.pov.curveshape == 'sphere_sweep' and not bezier_sweep:
            tab_write("union {\n")
            for spl in ob.data.splines:
                if spl.type != "BEZIER":
                    spl_type = "linear"
                    if spl.type == "NURBS":
                        spl_type = "cubic"
                    points = spl.points
                    num_points = len(points)
                    if spl.use_cyclic_u:
                        num_points += 3

                    tab_write("sphere_sweep { %s_spline %s,\n" % (spl_type, num_points))
                    if spl.use_cyclic_u:
                        pt1 = points[len(points) - 1]
                        wpt1 = pt1.co
                        tab_write(
                            "<%.4g,%.4g,%.4g>,%.4g\n"
                            % (wpt1[0], wpt1[1], wpt1[2], pt1.radius * ob.data.bevel_depth)
                        )
                    for pt in points:
                        wpt = pt.co
                        tab_write(
                            "<%.4g,%.4g,%.4g>,%.4g\n"
                            % (wpt[0], wpt[1], wpt[2], pt.radius * ob.data.bevel_depth)
                        )
                    if spl.use_cyclic_u:
                        for i in range(0, 2):
                            end_pt = points[i]
                            wpt = end_pt.co
                            tab_write(
                                "<%.4g,%.4g,%.4g>,%.4g\n"
                                % (wpt[0], wpt[1], wpt[2], end_pt.radius * ob.data.bevel_depth)
                            )

                tab_write("}\n")
        # below not used yet?
        if ob.pov.curveshape == 'sor':
            for spl in ob.data.splines:
                if spl.type in {'POLY', 'NURBS'}:
                    points = spl.points
                    num_points = len(points)
                    tab_write("sor { %s,\n" % num_points)
                    for pt in points:
                        wpt = pt.co
                        tab_write("<%.4g,%.4g>\n" % (wpt[0], wpt[1]))
                else:
                    tab_write("box { 0,0\n")
        if ob.pov.curveshape in {'lathe', 'prism'}:
            spl = ob.data.splines[0]
            if spl.type == "BEZIER":
                points = spl.bezier_points
                len_cur = len(points) - 1
                len_pts = len_cur * 4
                ifprism = ''
                if ob.pov.curveshape in {'prism'}:
                    height = ob.data.extrude
                    ifprism = '-%s, %s,' % (height, height)
                    len_cur += 1
                    len_pts += 4
                tab_write("%s { bezier_spline %s %s,\n" % (ob.pov.curveshape, ifprism, len_pts))
                for i in range(0, len_cur):
                    p1 = points[i].co
                    pR = points[i].handle_right
                    end = i + 1
                    if i == len_cur - 1 and ob.pov.curveshape in {'prism'}:
                        end = 0
                    pL = points[end].handle_left
                    p2 = points[end].co
                    line = "<%.4g,%.4g>" % (p1[0], p1[1])
                    line += "<%.4g,%.4g>" % (pR[0], pR[1])
                    line += "<%.4g,%.4g>" % (pL[0], pL[1])
                    line += "<%.4g,%.4g>" % (p2[0], p2[1])
                    tab_write("%s\n" % line)
            else:
                points = spl.points
                len_cur = len(points)
                len_pts = len_cur
                ifprism = ''
                if ob.pov.curveshape in {'prism'}:
                    height = ob.data.extrude
                    ifprism = '-%s, %s,' % (height, height)
                    len_pts += 3
                spl_type = 'quadratic'
                if spl.type == 'POLY':
                    spl_type = 'linear'
                tab_write(
                    "%s { %s_spline %s %s,\n" % (ob.pov.curveshape, spl_type, ifprism, len_pts)
                )
                if ob.pov.curveshape in {'prism'}:
                    pt = points[len(points) - 1]
                    wpt = pt.co
                    tab_write("<%.4g,%.4g>\n" % (wpt[0], wpt[1]))
                for pt in points:
                    wpt = pt.co
                    tab_write("<%.4g,%.4g>\n" % (wpt[0], wpt[1]))
                if ob.pov.curveshape in {'prism'}:
                    for i in range(2):
                        pt = points[i]
                        wpt = pt.co
                        tab_write("<%.4g,%.4g>\n" % (wpt[0], wpt[1]))
        if bezier_sweep:
            for p in range(len(ob.data.splines)):
                br = []
                depth = ob.data.bevel_depth
                spl = ob.data.splines[p]
                points = spl.bezier_points
                len_cur = len(points) - 1
                num_points = len_cur * 4
                if spl.use_cyclic_u:
                    len_cur += 1
                    num_points += 4
                tab_write("#declare %s_points_%s = array[%s]{\n" % (dataname, p, num_points))
                for i in range(len_cur):
                    p1 = points[i].co
                    pR = points[i].handle_right
                    end = i + 1
                    if spl.use_cyclic_u and i == (len_cur - 1):
                        end = 0
                    pL = points[end].handle_left
                    p2 = points[end].co
                    r3 = points[end].radius * depth
                    r0 = points[i].radius * depth
                    r1 = 2 / 3 * r0 + 1 / 3 * r3
                    r2 = 1 / 3 * r0 + 2 / 3 * r3
                    br.append((r0, r1, r2, r3))
                    line = "<%.4g,%.4g,%.4f>" % (p1[0], p1[1], p1[2])
                    line += "<%.4g,%.4g,%.4f>" % (pR[0], pR[1], pR[2])
                    line += "<%.4g,%.4g,%.4f>" % (pL[0], pL[1], pL[2])
                    line += "<%.4g,%.4g,%.4f>" % (p2[0], p2[1], p2[2])
                    tab_write("%s\n" % line)
                tab_write("}\n")
                tab_write("#declare %s_radii_%s = array[%s]{\n" % (dataname, p, len(br) * 4))
                for rad_tuple in br:
                    tab_write(
                        '%.4f,%.4f,%.4f,%.4f\n'
                        % (rad_tuple[0], rad_tuple[1], rad_tuple[2], rad_tuple[3])
                    )
                tab_write("}\n")
            if len(ob.data.splines) == 1:
                tab_write('#declare %s = object{\n' % dataname)
                tab_write(
                    '    Shape_Bezierpoints_Sphere_Sweep(yes,%s, %s_points_%s, %s_radii_%s) \n'
                    % (ob.data.resolution_u, dataname, p, dataname, p)
                )
            else:
                tab_write('#declare %s = union{\n' % dataname)
                for p in range(len(ob.data.splines)):
                    tab_write(
                        '    object{Shape_Bezierpoints_Sphere_Sweep(yes,%s, %s_points_%s, %s_radii_%s)} \n'
                        % (ob.data.resolution_u, dataname, p, dataname, p)
                    )
                # tab_write('#include "bezier_spheresweep.inc"\n') #now inlined
            # tab_write('#declare %s = object{Shape_Bezierpoints_Sphere_Sweep(yes,%s, %s_bezier_points, %.4f) \n'%(dataname,ob.data.resolution_u,dataname,ob.data.bevel_depth))
        if ob.pov.curveshape in {'loft'}:
            tab_write('object {MSM(%s,%s,"c",%s,"")\n' % (dataname, ob.pov.res_u, ob.pov.res_v))
        if ob.pov.curveshape in {'birail'}:
            splines = '%s1,%s2,%s3,%s4' % (dataname, dataname, dataname, dataname)
            tab_write('object {Coons(%s, %s, %s, "")\n' % (splines, ob.pov.res_u, ob.pov.res_v))
        pov_mat_name = "Default_texture"
        if ob.active_material:
            # pov_mat_name = string_strip_hyphen(bpy.path.clean_name(ob.active_material.name))
            try:
                material = ob.active_material
                write_object_material(material, ob, tab_write)
            except IndexError:
                print(ob.data)
        # tab_write("texture {%s}\n"%pov_mat_name)
        if ob.pov.curveshape in {'prism'}:
            tab_write("rotate <90,0,0>\n")
            tab_write("scale y*-1\n")
        tab_write("}\n")