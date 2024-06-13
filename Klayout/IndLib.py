import pya
import math

class PGS(pya.PCellDeclarationHelper):
    def __init__(self):
        super(PGS, self).__init__()

        self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(68, 20))
        self.param("r", self.TypeDouble, "radius", default = 100)
        

    def display_text_impl(self):
        return "PGS(R=" + ('%.1f' % self.r) + ")"
  
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

  
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
  
    def produce_impl(self):
        gr = self.layout.dbu # grid size
        
        r = self.r / gr
        w = 0.14 / gr # M1 minimum area
        s = 0.14 / gr # M1 minimal spacing
        
        n_arms = math.floor(r/(w+s))
        
        pts = []
        pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2,-w/2)))
        pts.append(pya.Point.from_dpoint(pya.DPoint( w/2,-w/2)))
        pts.append(pya.Point.from_dpoint(pya.DPoint( w/2, w/2)))
        pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, w/2)))
            
        self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
        
        for i in range(n_arms):
            # top right
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( -w/2+(w+s)*i, w/2+(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(  w/2+(w+s)*i, w/2+(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(  w/2+(w+s)*i, r)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -w/2+(w+s)*i, r)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( w/2+(w+s)*i, 2.5*w + (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( w/2+(w+s)*i, 1.5*w + (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( r          , 1.5*w + (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( r          , 2.5*w + (w+s)*i)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
            # bottom right
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( w/2+(w+s)*i, -w/2-(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( w/2+(w+s)*i,  w/2-(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( r          ,  w/2-(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( r          , -w/2-(w+s)*i)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( 2.5*w + (w+s)*i, -w/2-(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( 1.5*w + (w+s)*i, -w/2-(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( 1.5*w + (w+s)*i, -r)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( 2.5*w + (w+s)*i, -r)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
            # bottom left
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( -w/2-(w+s)*i, -w/2-(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(  w/2-(w+s)*i, -w/2-(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(  w/2-(w+s)*i, -r)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -w/2-(w+s)*i, -r)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( -w/2-(w+s)*i, -2.5*w - (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -w/2-(w+s)*i, -1.5*w - (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -r          , -1.5*w - (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -r          , -2.5*w - (w+s)*i)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
            # top left
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( -1.5*w-(w+s)*i, w/2+(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -2.5*w-(w+s)*i, w/2+(w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -2.5*w-(w+s)*i, r)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -1.5*w-(w+s)*i, r)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))
            
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint( -0.5*w-(w+s)*i, -0.5*w + (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -0.5*w-(w+s)*i,  0.5*w + (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -r          ,  0.5*w + (w+s)*i)))
            pts.append(pya.Point.from_dpoint(pya.DPoint( -r          , -0.5*w + (w+s)*i)))
            
            self.cell.shapes(self.l_layer).insert(pya.Polygon(pts))

class Oct_inductor(pya.PCellDeclarationHelper):
    def __init__(self):
        super(Oct_inductor, self).__init__()
        self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(72, 20))
        self.param("w", self.TypeDouble, "Line width", default = 10)
        self.param("r", self.TypeInt, "Radius", default = 100)
        self.param("s", self.TypeDouble, "Line separation", default = 15)
        self.param("f", self.TypeDouble, "Feed length", default = 15)

    def display_text_impl(self):
        return "octogonal inductor(N=1,R=" + ('%.1f' % self.r) + ",W=" + ('%.1f' % self.w) + ")"
  
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
  
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
  
    def produce_impl(self):
        gr = self.layout.dbu # grid size
        sep = self.s / gr
        wid = self.w / gr
        rad = self.r / gr
        fee = self.f / gr
        c_a = 1/(1+1/math.sqrt(2))
        
        pts = []
        pts.append(pya.Point.from_dpoint(pya.DPoint( sep/2, -rad-fee )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( sep/2, -rad )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( round(rad*c_a,-2), -rad )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( rad, -round(rad*c_a,-2) )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( rad, round(rad*c_a,-2) )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( round(rad*c_a,-2), rad )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( -round(rad*c_a,-2), rad )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( -rad, round(rad*c_a,-2) )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( -rad, -round(rad*c_a,-2) )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( -round(rad*c_a,-2),-rad )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( -sep/2, -rad )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( -sep/2, -rad-fee )))
        
        # create the shape
        self.cell.shapes(self.l_layer).insert(pya.Path(pts, self.w/gr))


class Square_inductor(pya.PCellDeclarationHelper):
    def __init__(self):
        # Important: initialize the super class
        super(Square_inductor, self).__init__()

        # declare the parameters
        self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(72, 20))
        self.param("w", self.TypeDouble, "Line width", default = 10)
        self.param("r", self.TypeDouble, "Radius", default = 50)
        self.param("d", self.TypeDouble, "Line separation", default = 10)
        self.param("f", self.TypeDouble, "feed length", default = 10)
        self.param("ct", self.TypeBoolean, "center tap", default = False)

    def display_text_impl(self):
        return "inductor(R=" + ('%.1f' % self.r) + ",w=" + ('%.1f' % self.w) + ",d=" + ('%.1f' % self.d) + ")"
  
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()
  
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
  
    def produce_impl(self):
        gr = self.layout.dbu
        
        path_nodes = []
        
        path_nodes.append(pya.Point.from_dpoint( pya.DPoint( -self.d/gr*(1+0.5*self.ct), -self.r/gr-self.f/gr ) ))
        path_nodes.append(pya.Point.from_dpoint( pya.DPoint( -self.d/gr*(1+0.5*self.ct), -self.r/gr ) ))
        path_nodes.append(pya.Point.from_dpoint( pya.DPoint( -self.r/gr,  -self.r/gr ) ))
        path_nodes.append(pya.Point.from_dpoint( pya.DPoint( -self.r/gr, self.r/gr ) ))
        if (self.ct == True):
            path_nodes.append(pya.Point.from_dpoint( pya.DPoint( 0, self.r/gr ) ))
            path_nodes.append(pya.Point.from_dpoint( pya.DPoint( 0, -self.r/gr-self.f/gr ) ))
            self.cell.shapes(self.l_layer).insert(pya.Path(path_nodes, self.w/gr))
            
            path_nodes = []
            path_nodes.append(pya.Point.from_dpoint( pya.DPoint( 0, -self.r/gr-self.f/gr ) ))
            path_nodes.append(pya.Point.from_dpoint( pya.DPoint( 0, self.r/gr ) ))
            path_nodes.append(pya.Point.from_dpoint( pya.DPoint( self.r/gr, self.r/gr ) ))
        else:
            path_nodes.append(pya.Point.from_dpoint( pya.DPoint( self.r/gr, self.r/gr ) ))
        path_nodes.append(pya.Point.from_dpoint( pya.DPoint( self.r/gr, -self.r/gr ) ))
        path_nodes.append(pya.Point.from_dpoint( pya.DPoint( self.d/gr*(1+0.5*self.ct), -self.r/gr ) ))
        path_nodes.append(pya.Point.from_dpoint( pya.DPoint( self.d/gr*(1+0.5*self.ct), -self.r/gr-self.f/gr ) ))
        
    # create the shape
        self.cell.shapes(self.l_layer).insert(pya.Path(path_nodes, self.w/gr))


        
class Oct_double_inductor(pya.PCellDeclarationHelper):

    def __init__(self):
        super(Oct_double_inductor, self).__init__()

        # declare the parameters
        self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(72, 20))
        self.param("w", self.TypeDouble, "Line width", default = 10)
        self.param("r", self.TypeDouble, "Radius", default = 100)
        self.param("s", self.TypeDouble, "Line separation", default = 5)
        self.param("f", self.TypeDouble, "Feed length", default = 5)
        self.param("ct", self.TypeBoolean, "center tap", default = False)
        
    def display_text_impl(self):
        return "octogonal inductor(N=2,R=" + ('%.1f' % self.r) + ",W=" + ('%.1f' % self.w) + ")"
        
    def can_create_from_shape_impl(self):
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

  
    def transformation_from_shape_impl(self):
        return pya.Trans(self.shape.bbox().center())
  
    def produce_impl(self):
        
        l_under = pya.LayerInfo(self.l.layer-1,20)
        l_via = pya.LayerInfo(self.l.layer-1,44)
        
        gr = self.layout.dbu # grid size
            # normalize to grid
        s = self.s / gr
        w = self.w / gr
        r = self.r / gr
        f = self.f / gr
        ct = self.ct
        
        via_w = 0.8 / gr
        via_d = 0.36 / gr
        via_s = 1.6 / gr
        
        c_a = 1/(1+1/math.sqrt(2))
        c_b = math.sqrt(2 + math.sqrt(2))/2
        
        ri = r-w-s
    
        
        # right port to underpass
        pts = []
        pts.append(pya.Point.from_dpoint( pya.DPoint( s+w*(1+ct)/2, -r-f) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( s+w*(1+ct)/2, -r) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( round(r*c_a,-2), -r) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( r, -round(r*c_a,-2) )))
        pts.append(pya.Point.from_dpoint( pya.DPoint( r, round(r*c_a,-2) )))
        pts.append(pya.Point.from_dpoint( pya.DPoint( round(r*c_a,-2), r )))
        pts.append(pya.Point.from_dpoint( pya.DPoint( round(r*c_a,-2), r )))
        pts.append(pya.Point.from_dpoint( pya.DPoint( round(r*c_a,-2), r )))
        pts.append(pya.Point.from_dpoint( pya.DPoint( w+s, r )))
        self.cell.shapes(self.layout.layer(self.l)).insert(pya.Path(pts, w))
        
        # other arm
        pts = []
        pts.append(pya.Point.from_dpoint( pya.DPoint( -w-s, ri ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -round(ri*c_a,-2), ri ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -ri, round(ri*c_a,-2) ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -ri, -round(ri*c_a,-2) ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -round(ri*c_a,-2), -ri ) ))
        
        if (ct):
            pts.append(pya.Point.from_dpoint( pya.DPoint( 0, -ri ) ))
            pts.append(pya.Point.from_dpoint( pya.DPoint( 0, -r-f ) ))
            self.cell.shapes(self.layout.layer(self.l)).insert(pya.Path(pts, w))
            pts = []
            pts.append(pya.Point.from_dpoint( pya.DPoint( 0, -r-f ) ))
            pts.append(pya.Point.from_dpoint( pya.DPoint( 0, -ri ) ))
        
        pts.append(pya.Point.from_dpoint( pya.DPoint( round(ri*c_a,-2), -ri ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( ri, -round(ri*c_a,-2) ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( ri, round(ri*c_a,-2) ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( round(ri*c_a,-2), ri ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( (w+s)/2, ri ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( (-w-s)/2, r ) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -round(r*c_a,-2), r) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -r, round(r*c_a,-2)) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -r, -round(r*c_a,-2)) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -round(r*c_a,-2), -r) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -s-w*(1+ct)/2, -r) ))
        pts.append(pya.Point.from_dpoint( pya.DPoint( -s-w*(1+ct)/2, -r-f) ))
        
        self.cell.shapes(self.layout.layer(self.l)).insert(pya.Path(pts, w))
        
        c_c = w*c_b/2
        
        # vias
        n_y = max( math.floor((w-2*via_d+via_w)/via_s), 1)
        n_x = max( math.floor((ri*c_a-c_c-w/2-s-2*via_d+via_w)/via_s), 1)
        
        exc_y = w - (2*n_y-1)*via_w - 2*via_d
        exc_x = (ri*c_a-c_c-w/2-s) - (2*n_x-1)*via_w - 2*via_d
        
        for i in range(n_y):
            for j in range(n_x):
                pts = []
                pts.append(pya.Point.from_dpoint(pya.DPoint( w+s + via_d + via_s*j + exc_x/2          ,r-via_d-via_s*i-exc_y/2 + w/2)))
                pts.append(pya.Point.from_dpoint(pya.DPoint( w+s + via_d + via_s*j + exc_x/2          ,r-via_d-via_w-via_s*i-exc_y/2 + w/2)))
                pts.append(pya.Point.from_dpoint(pya.DPoint( w+s + via_d + via_s*j + exc_x/2 + via_w  ,r-via_d-via_w-via_s*i-exc_y/2 + w/2)))
                pts.append(pya.Point.from_dpoint(pya.DPoint( w+s + via_d + via_s*j + exc_x/2 + via_w  ,r-via_d-via_s*i-exc_y/2 + w/2)))
        
                self.cell.shapes(self.layout.layer(l_via)).insert(pya.Polygon(pts))
                
                pts = []
                pts.append(pya.Point.from_dpoint(pya.DPoint( -w-s - via_d - via_s*j - exc_x/2          ,ri-via_d-via_s*i-exc_y/2 + w/2)))
                pts.append(pya.Point.from_dpoint(pya.DPoint( -w-s - via_d - via_s*j - exc_x/2          ,ri-via_d-via_w-via_s*i-exc_y/2 + w/2)))
                pts.append(pya.Point.from_dpoint(pya.DPoint( -w-s - via_d - via_s*j - exc_x/2 - via_w  ,ri-via_d-via_w-via_s*i-exc_y/2 + w/2)))
                pts.append(pya.Point.from_dpoint(pya.DPoint( -w-s - via_d - via_s*j - exc_x/2 - via_w  ,ri-via_d-via_s*i-exc_y/2 + w/2)))
        
                self.cell.shapes(self.layout.layer(l_via)).insert(pya.Polygon(pts))
        
        # underpass
        pts = []
        pts.append(pya.Point.from_dpoint(pya.DPoint( -ri*c_a-via_s, ri )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( -(w+s)/2, ri )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( (w+s)/2, r )))
        pts.append(pya.Point.from_dpoint(pya.DPoint( ri*c_a+via_s, r )))
        
        self.cell.shapes(self.layout.layer(l_under)).insert(pya.Path(pts, w))

class IndLib(pya.Library):

  def __init__(self):
  
    # Set the description
    self.description = "Inductor library"
    
    # Create the PCell declarations
    self.layout().register_pcell("1 turn Oct. Inductor", Oct_inductor())
    self.layout().register_pcell("1 turn Sqr. Inductor", Square_inductor())
    self.layout().register_pcell("2 turn Oct. Inductor", Oct_double_inductor())
    self.layout().register_pcell("Patterned Ground Shield", PGS())
    self.register("IndLib")


# Instantiate and register the library
IndLib()
