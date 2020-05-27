def dts_plot(filename,view_nd=3,colormap='coolwarm',auto_color=True,color_range=[0,100],auto_z=True,z_range=[0,100],max_pooling=True,k_size=[2,2]):

    import sys
    import os
    import numpy as np
    from vispy import app, scene, color
    import pandas as pd

    # ========================= User Inputs =======================================

    filename = filename     # dir as string i.e. "./datafile.csv\"

    view_nd = view_nd   # 3 for 3d surface plot, or 2 for 3d top view

    colormap = colormap   # 'coolwarm' (blue-white-red) or 'viridis' (green-yellow)
    auto_color = auto_color     # boolean
    color_range = color_range   # array, i.e. [0,100]

    auto_z = auto_z    # boolean
    z_range = z_range   # array, i.e. [0,100]

    max_pooling = max_pooling    # boolean
    k_size = k_size         # [1,2] to down sample distance data; [2,1] to down sample time data;
                            # [2,2] to down sample time and distance data

    # ========================= Theme Control =====================================

    z_xy_ratio = 1/1.5 # use value betwen [1/2, 1/1], 1/1.5 is suggested
    show_grid = True
    show_text = True
    show_axis = False   # not done yet, don't enable
    show_colorbar = True

    # ========================= No Change From Here ===============================
    # input check
    if not os.path.isfile(filename):
        print("Wrong Input of File Name!!!")
        print(filename)
        return "Wrong File Name"
    if not view_nd in [2,3]:
        print("Wrong Input of View Dimension!!!")
        print(view_nd)
        return "Wrong View Dimension"
    if z_range[1] <= z_range[0] or color_range[1] <= color_range[0]:
        print("Wrong Input of Temperautre or Color Range!!!")
        print(color_range,z_range)
        return "Wrong Temperautre or Color Range"

    # get data
    pz = pd.read_csv(filename, sep=',')
    col_name = list(pz.columns.values)
    first_col = col_name[0]
    distance_labels = col_name[1:]
    time_labels = pz[first_col]
    pz.drop(first_col,axis=1,inplace=True)
    z = np.array(pz)
    np.delete(z,0,0)

    if len(time_labels[0].split('-')) in [3,4,5,6]:
        new_time_labels = []
        for l in time_labels:
            _ = ['0000','00','00','00','00','00']
            for i,word in enumerate(l.split('-')):
                _[i] = str(word)
            if len(time_labels[0].split('-')) == 3:
                ll = ''+_[0]+'/'+_[1]+'/'+_[2]            
            if len(time_labels[0].split('-')) in [4,5]:
                ll = ''+_[0]+'/'+_[1]+'/'+_[2]+' '+_[3]+':'+_[4]
            if len(time_labels[0].split('-')) == 6:
                ll = ''+_[0]+'/'+_[1]+'/'+_[2]+' '+_[3]+':'+_[4]+':'+_[5]     
            new_time_labels.append(ll)
        time_labels = new_time_labels
        
    if auto_z:
        temp_labels = [np.amin(z), np.amax(z)]
    else:
        temp_labels = z_range
        
 
  
    

    if np.amin(z) == np.amax(z):
        auto_z = False
        auto_color = False
        
    if auto_color:
        color_range = [np.amin(z),np.amax(z)]
    else:
        color_range = color_range

    if auto_z:
        z_range = [np.amin(z),np.amax(z)]
    else:
        z_range = z_range

    if max_pooling:
        M, N = z.shape
        K, L = k_size
        MK = M // K
        NL = N // L
        if M%K == 1:
            new_row = z[MK * K:]
            z = np.vstack([z, new_row])
            MK = MK + 1
        if N%L == 1:
            new_col = z[:MK * K,NL * L:]
            z = np.hstack([z, new_col])
            NL = NL + 1

        z = z[:MK * K, :NL * L].reshape(MK, K, NL, L).max(axis=(1, 3))
        
    # normalize color (mustn't change order of normalize color and data)
    cnorm = (z - color_range[0]) / (abs(color_range[1] - color_range[0]))
    c = color.get_colormap(colormap).map(cnorm)
    c = c.flatten().tolist()
    c=list(map(lambda x,y,z,w:(x,y,z,w), c[0::4],c[1::4],c[2::4],c[3::4]))

    # normalize data
    xnorm = z.shape[0]
    ynorm = z.shape[1]
    znorm = abs(z_range[1] - z_range[0]) 
    z = z - z_range[0]

    # set cemara
    canvas = scene.SceneCanvas(keys='interactive', bgcolor='black')
    view = canvas.central_widget.add_view()
    if view_nd == 3:
        view.camera = scene.TurntableCamera(up='z',fov=30,distance=3,azimuth=60,elevation=40)
    else:
        view.camera = scene.PanZoomCamera(aspect =1,rect=(-0.7,-0.7,1.4,1.4))

    # surface plot, centered at [0,0,0], size [1,1,1]    
    p1 = scene.visuals.SurfacePlot(z=z)
    p1.mesh_data.set_vertex_colors(c)
    p1.transform = scene.transforms.MatrixTransform()
    p1.transform.scale([1/xnorm, 1/ynorm, 1/znorm])
    p1.transform.translate([-0.5,-0.5, -0.5])
    p1.transform.scale([1, 1, z_xy_ratio])
    view.add(p1)

    # background grid
    if view_nd == 3 and show_grid :
        zplane = scene.visuals.Plane(direction='+z',color='grey',edge_color='w',width=1,height=1,parent=view.scene,width_segments=10,height_segments=10)
        zplane.transform = scene.transforms.MatrixTransform()
        zplane.transform.translate([0,0, -0.5])
        zplane.transform.scale([1,1, z_xy_ratio])
        
        xplane = scene.visuals.Plane(direction='+x',color='grey',edge_color='w',width=1,height=1,parent=view.scene,width_segments=10,height_segments=10)
        xplane.transform = scene.transforms.MatrixTransform()
        xplane.transform.translate([-0.5,0, 0])
        xplane.transform.scale([1,1, z_xy_ratio])

        yplane = scene.visuals.Plane(direction='+y',color='grey',edge_color='w',width=1,height=1,parent=view.scene,width_segments=10,height_segments=10)
        yplane.transform = scene.transforms.MatrixTransform()
        yplane.transform.translate([0,0.5, 0])    
        yplane.transform.scale([1,1, z_xy_ratio])
        
    # XYZ axis, not done yet, don't enable
    if show_axis:
        axis = scene.visuals.XYZAxis(parent=view.scene)    
        
    # alternative XYZ axis, text and labels
    if show_text:
        time_marks,distance_marks,temp_marks = ([] for i in range(3))
        time_pos,distance_pos, temp_pos = ([] for i in range(3))

        if view_nd == 3:
            for n in range(11):
                time_marks.append(time_labels[int((len(time_labels)-1)*n/10)])
                distance_marks.append(distance_labels[int((len(distance_labels)-1)*n/10)])
                temp_marks.append(str(round(abs(temp_labels[1]-temp_labels[0])*n/10 + temp_labels[0],1)))

                time_pos.append([n/10-0.5,-0.51,-0.5*z_xy_ratio])
                distance_pos.append([0.51,n/10-0.5,-0.5*z_xy_ratio])
                temp_pos.append([0.5,0.51,(n/10-0.5)*z_xy_ratio])

            font_size = 24
            
            xlabel = scene.visuals.Text(text=time_marks,pos=time_pos,font_size=font_size,bold=True,color='w',parent=view.scene,anchor_x='right')
            xtext = scene.visuals.Text(text='Time',pos=[0,-0.7,-0.5*z_xy_ratio],font_size=font_size,bold=True,color='w',parent=view.scene,anchor_x='right')    
            ylabel = scene.visuals.Text(text=distance_marks,pos=distance_pos,font_size=font_size,bold=True,color='w',parent=view.scene,anchor_y='top')
            ytext = scene.visuals.Text(text='Distance (m)',pos=[0.6,0,-0.5*z_xy_ratio],font_size=font_size,bold=True,color='w',parent=view.scene,anchor_y='top')
            zlabel = scene.visuals.Text(text=temp_marks,pos=temp_pos,font_size=font_size,bold=True,color='w',parent=view.scene,anchor_x='left')    
            ztext = scene.visuals.Text(text='Temperature (°C)',pos=[0.5,0.5,0.6*z_xy_ratio],font_size=font_size,bold=True,color='w',parent=view.scene)
                
        if view_nd == 2:
            for n in range(11):
                time_marks.append(time_labels[int((len(time_labels)-1)*n/10)])
                distance_marks.append(distance_labels[int((len(distance_labels)-1)*n/10)])

                time_pos.append([n/10-0.5,-0.51,-0.5*z_xy_ratio])
                distance_pos.append([0.51,n/10-0.5,-0.5*z_xy_ratio])
        
            font_size = 8
            anchor_x = 'left'
            
            xlabel = scene.visuals.Text(text=time_marks,pos=time_pos,font_size=font_size,bold=True,color='w',parent=view.scene,anchor_x='left',rotation=30)
            xtext = scene.visuals.Text(text='Time',pos=[0,-0.65,-0.5*z_xy_ratio],font_size=font_size,bold=True,color='w',parent=view.scene,anchor_y='top')    
            ylabel = scene.visuals.Text(text=distance_marks,pos=distance_pos,font_size=font_size,bold=True,color='w',parent=view.scene,anchor_x='left')
            ytext = scene.visuals.Text(text='Distance (m)',pos=[0.6,0,-0.5*z_xy_ratio],font_size=font_size,bold=True,color='w',parent=view.scene,anchor_x='left',rotation=90)
         
    # if sys.flags.interactive == 0:
    #     app.run()
    return canvas


