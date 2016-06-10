import unittest
import numpy

from srxraylib.waveoptics.wavefront import Wavefront1D
from srxraylib.waveoptics.wavefront2D import Wavefront2D


do_plot = 1

#
# 1D tests
#
class Wavefront1DTest(unittest.TestCase):


    def test_initializers(self,do_plot=do_plot):

        print("#                                                             ")
        print("# Tests for initializars (1D)                                 ")
        print("#                                                             ")

        x = numpy.linspace(-100,100,50)
        y = numpy.abs(x)**1.5 +  1j*numpy.abs(x)**1.8



        wf0 = Wavefront1D.initialize_wavefront_from_steps(x[0],numpy.abs(x[1]-x[0]),y.size)
        wf0.set_complex_amplitude(y)

        wf1 = Wavefront1D.initialize_wavefront_from_range(x[0],x[-1],y.size)
        wf1.set_complex_amplitude(y)

        wf2 = Wavefront1D.initialize_wavefront_from_arrays(x,y)

        print("wavefront sizes: ",wf1.size(),wf1.size(),wf2.size())

        if do_plot:
            from srxraylib.plot.gol import plot
            plot(wf0.get_abscissas(),wf0.get_intensity(),
                       title="initialize_wavefront_from_steps",show=0)
            plot(wf1.get_abscissas(),wf1.get_intensity(),
                       title="initialize_wavefront_from_range",show=0)
            plot(wf2.get_abscissas(),wf2.get_intensity(),
                       title="initialize_wavefront_from_arrays",show=1)

        numpy.testing.assert_almost_equal(wf0.get_intensity(),wf1.get_intensity(),5)
        numpy.testing.assert_almost_equal(wf0.get_intensity(),wf2.get_intensity(),5)

    def test_plane_wave(self,do_plot=do_plot):
        #
        # plane wave
        #
        print("#                                                             ")
        print("# Tests for a 1D plane wave                                   ")
        print("#                                                             ")

        wavelength        = 1.24e-10

        wavefront_length_x = 400e-6

        npixels_x =  1024

        pixelsize_x = wavefront_length_x / npixels_x



        wavefront = Wavefront1D.initialize_wavefront_from_steps(
                        x_start=-0.5*wavefront_length_x,x_step=pixelsize_x,
                        number_of_points=npixels_x,wavelength=wavelength)

        # possible modifications

        wavefront.set_plane_wave_from_amplitude_and_phase(5.0,numpy.pi/2)
        numpy.testing.assert_almost_equal(wavefront.get_intensity(),25,5)

        wavefront.set_plane_wave_from_complex_amplitude(2.0+3j)
        numpy.testing.assert_almost_equal(wavefront.get_intensity(),13,5)

        phase_before = wavefront.get_phase()
        wavefront.add_phase_shift(numpy.pi/2)
        phase_after = wavefront.get_phase()
        numpy.testing.assert_almost_equal(phase_before+numpy.pi/2,phase_after,5)

        intensity_before = wavefront.get_intensity()
        wavefront.rescale_amplitude(10.0)
        intensity_after = wavefront.get_intensity()
        numpy.testing.assert_almost_equal(intensity_before*100,intensity_after,5)

        # interpolation

        wavefront.set_plane_wave_from_complex_amplitude(2.0+3j)
        test_value1 = wavefront.get_interpolated_complex_amplitude(0.01)
        self.assertAlmostEqual( (2.0+3j).real, test_value1.real, 5)
        self.assertAlmostEqual( (2.0+3j).imag, test_value1.imag, 5)


        if do_plot:
            from srxraylib.plot.gol import plot
            plot(wavefront.get_abscissas(),wavefront.get_intensity(),title="Intensity (plane wave)",show=0)
            plot(wavefront.get_abscissas(),wavefront.get_phase(),title="Phase (plane wave)",show=1)


    def test_spherical_wave(self,do_plot=do_plot):
        #
        # plane wave
        #
        print("#                                                             ")
        print("# Tests for a 1D spherical wave                               ")
        print("#                                                             ")

        wavelength        = 1.24e-10

        wavefront_length_x = 400e-6

        npixels_x =  1024

        pixelsize_x = wavefront_length_x / npixels_x



        wf1 = Wavefront1D.initialize_wavefront_from_steps(
                        x_start=-0.5*wavefront_length_x,x_step=pixelsize_x,
                        number_of_points=npixels_x,wavelength=wavelength)

        wf2 = Wavefront1D.initialize_wavefront_from_steps(
                        x_start=-0.5*wavefront_length_x,x_step=pixelsize_x,
                        number_of_points=npixels_x,wavelength=wavelength)

        # an spherical wavefront is obtained 1) by creation, 2) focusing a planewave

        wf1.set_spherical_wave(-5.0, 3+0j)
        wf1.apply_slit(-50e-6,10e-6)

        wf2.set_plane_wave_from_complex_amplitude(3+0j)
        wf2.apply_ideal_lens(5.0)
        wf2.apply_slit(-50e-6,10e-6)



        if do_plot:
            from srxraylib.plot.gol import plot
            plot(wf1.get_abscissas(),wf1.get_phase(),title="Phase of spherical wavefront",show=0)
            plot(wf2.get_abscissas(),wf2.get_phase(),title="Phase of focused plane wavefront",show=0)
            plot(wf1.get_abscissas(),wf1.get_phase(from_minimum_intensity=0.1),title="Phase of spherical wavefront (for intensity > 0.1)",show=0)
            plot(wf2.get_abscissas(),wf2.get_phase(from_minimum_intensity=0.1),title="Phase of focused plane wavefront (for intensity > 0.1)",show=1)


        numpy.testing.assert_almost_equal(wf1.get_phase(),wf2.get_phase(),5)

    def test_interpolator(self,do_plot=do_plot):
        #
        # interpolator
        #
        print("#                                                             ")
        print("# Tests for 1D interpolator                                   ")
        print("#                                                             ")

        x = numpy.linspace(-10,10,100)

        sigma = 3.0
        Z = numpy.exp(-1.0*x**2/2/sigma**2)

        print("shape of Z",Z.shape)

        wf = Wavefront1D.initialize_wavefront_from_steps(x[0],numpy.abs(x[1]-x[0]),number_of_points=100)
        print("wf shape: ",wf.size())
        wf.set_complex_amplitude( Z )

        x1 = 3.2
        z1 = numpy.exp(x1**2/-2/sigma**2)
        print("complex ampl at (%g): %g+%gi (exact=%g)"%(x1,
                                                        wf.get_interpolated_complex_amplitude(x1).real,
                                                        wf.get_interpolated_complex_amplitude(x1).imag,
                                                        z1))
        self.assertAlmostEqual(wf.get_interpolated_complex_amplitude(x1).real,z1,4)

        print("intensity  at (%g):   %g (exact=%g)"%(x1,wf.get_interpolated_intensity(x1),z1**2))
        self.assertAlmostEqual(wf.get_interpolated_intensity(x1),z1**2,4)


        if do_plot:
            from srxraylib.plot.gol import plot
            plot(wf.get_abscissas(),wf.get_intensity(),title="Original",show=1)
            xx = wf.get_abscissas()
            yy = wf.get_interpolated_intensities(wf.get_abscissas()-1e-5)
            plot(xx,yy,title="interpolated on same grid",show=1)


#
# 2D tests
#

class Wavefront2DTest(unittest.TestCase):

    def test_initializers(self,do_plot=do_plot):

        print("#                                                             ")
        print("# Tests for initializars (2D)                                 ")
        print("#                                                             ")

        x = numpy.linspace(-100,100,50)
        y = numpy.linspace(-50,50,200)
        XY = numpy.meshgrid(x,y)
        X = XY[0].T
        Y = XY[1].T
        sigma = 10
        Z = numpy.exp(- (X**2 + Y**2)/2/sigma**2) * 1j
        print("Shapes x,y,z: ",x.shape,y.shape,Z.shape)

        wf0 = Wavefront2D.initialize_wavefront_from_steps(x[0],x[1]-x[0],y[0],y[1]-y[0],number_of_points=Z.shape)
        wf0.set_complex_amplitude(Z)

        wf1 = Wavefront2D.initialize_wavefront_from_range(x[0],x[-1],y[0],y[-1],number_of_points=Z.shape)
        wf1.set_complex_amplitude(Z)

        wf2 = Wavefront2D.initialize_wavefront_from_arrays(x,y,Z)

        if do_plot:
            from srxraylib.plot.gol import plot_image
            plot_image(wf0.get_intensity(),wf0.get_coordinate_x(),wf0.get_coordinate_y(),
                       title="initialize_wavefront_from_steps",show=0)
            plot_image(wf1.get_intensity(),wf1.get_coordinate_x(),wf1.get_coordinate_y(),
                       title="initialize_wavefront_from_range",show=0)
            plot_image(wf2.get_intensity(),wf2.get_coordinate_x(),wf2.get_coordinate_y(),
                       title="initialize_wavefront_from_arrays",show=1)

        numpy.testing.assert_almost_equal(wf0.get_intensity(),wf1.get_intensity(),7)
        numpy.testing.assert_almost_equal(wf0.get_intensity(),wf2.get_intensity(),7)
        numpy.testing.assert_almost_equal(wf0.get_coordinate_x(),wf1.get_coordinate_x(),7)
        numpy.testing.assert_almost_equal(wf0.get_coordinate_x(),wf2.get_coordinate_x(),7)
        numpy.testing.assert_almost_equal(wf0.get_coordinate_y(),wf1.get_coordinate_y(),7)
        numpy.testing.assert_almost_equal(wf0.get_coordinate_y(),wf2.get_coordinate_y(),7)


    def test_plane_wave(self,do_plot=do_plot):
        #
        # plane wave
        #
        print("#                                                             ")
        print("# Tests for a 2D plane wave                                      ")
        print("#                                                             ")

        wavelength        = 1.24e-10

        wavefront_length_x = 400e-6
        wavefront_length_y = wavefront_length_x

        npixels_x =  1024
        npixels_y =  npixels_x

        pixelsize_x = wavefront_length_x / npixels_x
        pixelsize_y = wavefront_length_y / npixels_y



        wavefront = Wavefront2D.initialize_wavefront_from_steps(
                        x_start=-0.5*wavefront_length_x,x_step=pixelsize_x,
                        y_start=-0.5*wavefront_length_y,y_step=pixelsize_y,
                        number_of_points=(npixels_x,npixels_y),wavelength=wavelength)

        # possible modifications

        wavefront.set_plane_wave_from_amplitude_and_phase(5.0,numpy.pi/2)
        numpy.testing.assert_almost_equal(wavefront.get_intensity(),25,5)

        wavefront.set_plane_wave_from_complex_amplitude(2.0+3j)
        numpy.testing.assert_almost_equal(wavefront.get_intensity(),13,5)

        phase_before = wavefront.get_phase()
        wavefront.add_phase_shift(numpy.pi/2)
        phase_after = wavefront.get_phase()
        numpy.testing.assert_almost_equal(phase_before+numpy.pi/2,phase_after,5)

        intensity_before = wavefront.get_intensity()
        wavefront.rescale_amplitude(10.0)
        intensity_after = wavefront.get_intensity()
        numpy.testing.assert_almost_equal(intensity_before*100,intensity_after,5)

        # interpolation

        wavefront.set_plane_wave_from_complex_amplitude(2.0+3j)
        test_value1 = wavefront.get_interpolated_complex_amplitude(0.01,1.3)
        self.assertAlmostEqual( (2.0+3j).real, test_value1.real, 5)
        self.assertAlmostEqual( (2.0+3j).imag, test_value1.imag, 5)


        if do_plot:
            from srxraylib.plot.gol import plot_image
            plot_image(wavefront.get_intensity(),wavefront.get_coordinate_x(),wavefront.get_coordinate_y(),
                       title="Intensity (plane wave)",show=0)
            plot_image(wavefront.get_phase(),wavefront.get_coordinate_x(),wavefront.get_coordinate_y(),
                       title="Phase (plane wave)",show=1)



    def test_spherical_wave(self,do_plot=do_plot):
        #
        # plane wave
        #
        print("#                                                             ")
        print("# Tests for a 2D spherical wave                               ")
        print("#                                                             ")

        wavelength        = 1.24e-10

        wavefront_length_x = 400e-6
        wavefront_length_y = wavefront_length_x

        npixels_x =  1024
        npixels_y =  npixels_x

        pixelsize_x = wavefront_length_x / npixels_x
        pixelsize_y = wavefront_length_y / npixels_y



        wf1 = Wavefront2D.initialize_wavefront_from_steps(
                        x_start=-0.5*wavefront_length_x,x_step=pixelsize_x,
                        y_start=-0.5*wavefront_length_y,y_step=pixelsize_y,
                        number_of_points=(npixels_x,npixels_y),wavelength=wavelength)

        wf2 = Wavefront2D.initialize_wavefront_from_steps(
                        x_start=-0.5*wavefront_length_x,x_step=pixelsize_x,
                        y_start=-0.5*wavefront_length_y,y_step=pixelsize_y,
                        number_of_points=(npixels_x,npixels_y),wavelength=wavelength)

        # an spherical wavefront is obtained 1) by creation, 2) focusing a planewave

        wf1.set_spherical_wave(-5.0, 3+0j)
        wf1.apply_slit(-50e-6,10e-6,-20e-6,40e-6)

        wf2.set_plane_wave_from_complex_amplitude(3+0j)
        wf2.apply_ideal_lens(5.0,5.0)
        wf2.apply_slit(-50e-6,10e-6,-20e-6,40e-6)



        if do_plot:
            from srxraylib.plot.gol import plot_image
            plot_image(wf1.get_phase(),wf2.get_coordinate_x(),wf2.get_coordinate_y(),
                       title="Phase of spherical wavefront",show=0)
            plot_image(wf2.get_phase(),wf2.get_coordinate_x(),wf2.get_coordinate_y(),
                       title="Phase of focused plane wavefront",show=0)
            plot_image(wf1.get_phase(from_minimum_intensity=0.1),wf2.get_coordinate_x(),wf2.get_coordinate_y(),
                       title="Phase of spherical wavefront (for intensity > 0.1)",show=0)
            plot_image(wf2.get_phase(from_minimum_intensity=0.1),wf2.get_coordinate_x(),wf2.get_coordinate_y(),
                       title="Phase of focused plane wavefront (for intensity > 0.1)",show=1)


        numpy.testing.assert_almost_equal(wf1.get_phase(),wf2.get_phase(),5)


    def test_interpolator(self,do_plot=do_plot):
        #
        # interpolator
        #
        print("#                                                             ")
        print("# Tests for 2D interpolator                                   ")
        print("#                                                             ")

        x = numpy.linspace(-10,10,100)
        y = numpy.linspace(-20,20,50)

        xy = numpy.meshgrid(x,y)
        X = xy[0].T
        Y = xy[1].T
        sigma = 3.0
        Z = numpy.exp(- (X**2+Y**2)/2/sigma**2)

        print("shape of Z",Z.shape)

        wf = Wavefront2D.initialize_wavefront_from_steps(x[0],x[1]-x[0],y[0],y[1]-y[0],number_of_points=(100,50))
        print("wf shape: ",wf.size())
        wf.set_complex_amplitude( Z )

        x1 = 3.2
        y1 = -2.5
        z1 = numpy.exp(- (x1**2+y1**2)/2/sigma**2)
        print("complex ampl at (%g,%g): %g+%gi (exact=%g)"%(x1,y1,
                                                        wf.get_interpolated_complex_amplitude(x1,y1).real,
                                                        wf.get_interpolated_complex_amplitude(x1,y1).imag,
                                                        z1))
        self.assertAlmostEqual(wf.get_interpolated_complex_amplitude(x1,y1).real,z1,5)

        print("intensity  at (%g,%g):   %g (exact=%g)"%(x1,y1,wf.get_interpolated_intensity(x1,y1),z1**2))
        self.assertAlmostEqual(wf.get_interpolated_intensity(x1,y1),z1**2,5)


        if do_plot:
            from srxraylib.plot.gol import plot_image
            plot_image(wf.get_intensity(),wf.get_coordinate_x(),wf.get_coordinate_y(),title="Original",show=0)
            plot_image(wf.get_interpolated_intensity(X,Y),wf.get_coordinate_x(),wf.get_coordinate_y(),
                       title="interpolated on same grid",show=1)

















