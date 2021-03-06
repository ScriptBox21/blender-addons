# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
"""Get some Blender particle objects translated to POV."""

import bpy


def export_hair(file, ob, p_sys, global_matrix, write_matrix):
    """Get Blender path particles (hair strands) objects translated to POV sphere_sweep unions."""
    # tstart = time.time()
    textured_hair = 0
    if ob.material_slots[p_sys.settings.material - 1].material and ob.active_material is not None:
        pmaterial = ob.material_slots[p_sys.settings.material - 1].material
        # XXX Todo: replace by pov_(Particles?)_texture_slot
        for th in pmaterial.pov_texture_slots:
            povtex = th.texture  # slot.name
            tex = bpy.data.textures[povtex]

            if th and th.use:
                if (tex.type == 'IMAGE' and tex.image) or tex.type != 'IMAGE':
                    if th.use_map_color_diffuse:
                        textured_hair = 1
        if pmaterial.strand.use_blender_units:
            strand_start = pmaterial.strand.root_size
            strand_end = pmaterial.strand.tip_size
            strand_shape = pmaterial.strand.shape
        else:  # Blender unit conversion
            strand_start = pmaterial.strand.root_size / 200.0
            strand_end = pmaterial.strand.tip_size / 200.0
            strand_shape = pmaterial.strand.shape
    else:
        pmaterial = "default"  # No material assigned in blender, use default one
        strand_start = 0.01
        strand_end = 0.01
        strand_shape = 0.0
    # Set the number of particles to render count rather than 3d view display
    # p_sys.set_resolution(scene, ob, 'RENDER') # DEPRECATED
    # When you render, the entire dependency graph will be
    # evaluated at render resolution, including the particles.
    # In the viewport it will be at viewport resolution.
    # So there is no need fo render engines to use this function anymore,
    # it's automatic now.
    steps = p_sys.settings.display_step
    steps = 2 ** steps  # or + 1 # Formerly : len(particle.hair_keys)

    total_number_of_strands = p_sys.settings.count + p_sys.settings.rendered_child_count
    # hairCounter = 0
    file.write('#declare HairArray = array[%i] {\n' % total_number_of_strands)
    for pindex in range(0, total_number_of_strands):

        # if particle.is_exist and particle.is_visible:
        # hairCounter += 1
        # controlPointCounter = 0
        # Each hair is represented as a separate sphere_sweep in POV-Ray.

        file.write('sphere_sweep{')
        if p_sys.settings.use_hair_bspline:
            file.write('b_spline ')
            file.write(
                '%i,\n' % (steps + 2)
            )  # +2 because the first point needs tripling to be more than a handle in POV
        else:
            file.write('linear_spline ')
            file.write('%i,\n' % (steps))
        # changing world coordinates to object local coordinates by
        # multiplying with inverted matrix
        init_coord = ob.matrix_world.inverted() @ (p_sys.co_hair(ob, particle_no=pindex, step=0))
        if (
            ob.material_slots[p_sys.settings.material - 1].material
            and ob.active_material is not None
        ):
            pmaterial = ob.material_slots[p_sys.settings.material - 1].material
            for th in pmaterial.pov_texture_slots:
                if th and th.use and th.use_map_color_diffuse:
                    povtex = th.texture  # slot.name
                    tex = bpy.data.textures[povtex]
                    # treat POV textures as bitmaps
                    if (
                        tex.type == 'IMAGE'
                        and tex.image
                        and th.texture_coords == 'UV'
                        and ob.data.uv_textures is not None
                    ):
                        # or (
                        # tex.pov.tex_pattern_type != 'emulator'
                        # and th.texture_coords == 'UV'
                        # and ob.data.uv_textures is not None
                        # ):
                        image = tex.image
                        image_width = image.size[0]
                        image_height = image.size[1]
                        image_pixels = image.pixels[:]
                        uv_co = p_sys.uv_on_emitter(mod, p_sys.particles[pindex], pindex, 0)
                        x_co = round(uv_co[0] * (image_width - 1))
                        y_co = round(uv_co[1] * (image_height - 1))
                        pixelnumber = (image_width * y_co) + x_co
                        r = image_pixels[pixelnumber * 4]
                        g = image_pixels[pixelnumber * 4 + 1]
                        b = image_pixels[pixelnumber * 4 + 2]
                        a = image_pixels[pixelnumber * 4 + 3]
                        init_color = (r, g, b, a)
                    else:
                        # only overwrite variable for each competing texture for now
                        init_color = tex.evaluate((init_coord[0], init_coord[1], init_coord[2]))
        for step in range(0, steps):
            coord = ob.matrix_world.inverted() @ (p_sys.co_hair(ob, particle_no=pindex, step=step))
            # for controlPoint in particle.hair_keys:
            if p_sys.settings.clump_factor != 0:
                hair_strand_diameter = p_sys.settings.clump_factor / 200.0 * random.uniform(0.5, 1)
            elif step == 0:
                hair_strand_diameter = strand_start
            else:
                hair_strand_diameter += (strand_end - strand_start) / (
                    p_sys.settings.display_step + 1
                )  # XXX +1 or not? # XXX use strand_shape in formula
            if step == 0 and p_sys.settings.use_hair_bspline:
                # Write three times the first point to compensate pov Bezier handling
                file.write(
                    '<%.6g,%.6g,%.6g>,%.7g,\n'
                    % (coord[0], coord[1], coord[2], abs(hair_strand_diameter))
                )
                file.write(
                    '<%.6g,%.6g,%.6g>,%.7g,\n'
                    % (coord[0], coord[1], coord[2], abs(hair_strand_diameter))
                )
                # Useless because particle location is the tip, not the root:
                # file.write(
                # '<%.6g,%.6g,%.6g>,%.7g'
                # % (
                # particle.location[0],
                # particle.location[1],
                # particle.location[2],
                # abs(hair_strand_diameter)
                # )
                # )
                # file.write(',\n')
            # controlPointCounter += 1
            # total_number_of_strands += len(p_sys.particles)# len(particle.hair_keys)

            # Each control point is written out, along with the radius of the
            # hair at that point.
            file.write(
                '<%.6g,%.6g,%.6g>,%.7g' % (coord[0], coord[1], coord[2], abs(hair_strand_diameter))
            )

            # All coordinates except the last need a following comma.

            if step != steps - 1:
                file.write(',\n')
            else:
                if textured_hair:
                    # Write pigment and alpha (between Pov and Blender,
                    # alpha 0 and 1 are reversed)
                    file.write(
                        '\npigment{ color srgbf < %.3g, %.3g, %.3g, %.3g> }\n'
                        % (init_color[0], init_color[1], init_color[2], 1.0 - init_color[3])
                    )
                # End the sphere_sweep declaration for this hair
                file.write('}\n')

        # All but the final sphere_sweep (each array element) needs a terminating comma.
        if pindex != total_number_of_strands:
            file.write(',\n')
        else:
            file.write('\n')

    # End the array declaration.

    file.write('}\n')
    file.write('\n')

    if not textured_hair:
        # Pick up the hair material diffuse color and create a default POV-Ray hair texture.

        file.write('#ifndef (HairTexture)\n')
        file.write('  #declare HairTexture = texture {\n')
        file.write(
            '    pigment {srgbt <%s,%s,%s,%s>}\n'
            % (
                pmaterial.diffuse_color[0],
                pmaterial.diffuse_color[1],
                pmaterial.diffuse_color[2],
                (pmaterial.strand.width_fade + 0.05),
            )
        )
        file.write('  }\n')
        file.write('#end\n')
        file.write('\n')

    # Dynamically create a union of the hairstrands (or a subset of them).
    # By default use every hairstrand, commented line is for hand tweaking test renders.
    file.write('//Increasing HairStep divides the amount of hair for test renders.\n')
    file.write('#ifndef(HairStep) #declare HairStep = 1; #end\n')
    file.write('union{\n')
    file.write('  #local I = 0;\n')
    file.write('  #while (I < %i)\n' % total_number_of_strands)
    file.write('    object {HairArray[I]')
    if not textured_hair:
        file.write(' texture{HairTexture}\n')
    else:
        file.write('\n')
    # Translucency of the hair:
    file.write('        hollow\n')
    file.write('        double_illuminate\n')
    file.write('        interior {\n')
    file.write('            ior 1.45\n')
    file.write('            media {\n')
    file.write('                scattering { 1, 10*<0.73, 0.35, 0.15> /*extinction 0*/ }\n')
    file.write('                absorption 10/<0.83, 0.75, 0.15>\n')
    file.write('                samples 1\n')
    file.write('                method 2\n')
    file.write('                density {cylindrical\n')
    file.write('                    color_map {\n')
    file.write('                        [0.0 rgb <0.83, 0.45, 0.35>]\n')
    file.write('                        [0.5 rgb <0.8, 0.8, 0.4>]\n')
    file.write('                        [1.0 rgb <1,1,1>]\n')
    file.write('                    }\n')
    file.write('                }\n')
    file.write('            }\n')
    file.write('        }\n')
    file.write('    }\n')

    file.write('    #local I = I + HairStep;\n')
    file.write('  #end\n')

    write_matrix(global_matrix @ ob.matrix_world)

    file.write('}')
    print('Totals hairstrands written: %i' % total_number_of_strands)
    print('Number of tufts (particle systems)', len(ob.particle_systems))

    # Set back the displayed number of particles to preview count
    # p_sys.set_resolution(scene, ob, 'PREVIEW') #DEPRECATED
    # When you render, the entire dependency graph will be
    # evaluated at render resolution, including the particles.
    # In the viewport it will be at viewport resolution.
    # So there is no need fo render engines to use this function anymore,
    # it's automatic now.
