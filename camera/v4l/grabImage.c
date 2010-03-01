#include <Python.h>
#include "../vision/vision.h"
#include "v4lcap.h"

/*********
 * Arguments: (string device_name,
 *             int width,
 *             int height
 *             int color)
 *
 *   Color is a true/false value.  For now, if color is true,
 *    the image will be in 24 bpp color, and if it's false, it
 *    will be in 8 bpp greyscale.
 *
 * Returns: (int size, int bpp, int handle, buffer data)
 *          handle is the file handle for the image capture
 *          device, and it needs to get passed back to the
 *          C level for refresh and free operations.
 *********/

static PyObject *grab_image(PyObject *self, PyObject *args){
  char *device;
  int width, height, color, channel;
  struct image_cap *image;
  PyObject *buffer, *tuple;

  //Expects grab_image(device_name, width, height, color, channel)
  if(!PyArg_ParseTuple(args, "siiii", &device, &width, &height, &color, &channel)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to grab_image");
    return NULL;
  }

  image = Cgrab_image(device, width, height, color, channel);
  if (image == NULL){
    PyErr_SetString(PyExc_IOError, "Error in C function call");
    return NULL;
  }

  buffer = PyBuffer_FromMemory(image->data, image->size);

  tuple = Py_BuildValue("iiiO", image->size, image->bpp, image->handle, buffer);

  free(image);

  return tuple;
}

//Free the buffer given by grab_image
//Expects free_image(handle, buffer)
//Returns 0 for success
static PyObject *free_image(PyObject *self, PyObject *args){
  PyObject *obj, *buffer;
  int dev;
  struct image_cap *image_struct;

  //Get the buffer object from the arguments
  if (!PyArg_ParseTuple(args, "iO", &dev, &obj)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to free_image");
    return NULL;
  }

  //Make sure it's a valid buffer object
  if (!PyBuffer_Check(obj)){
    PyErr_SetString(PyExc_TypeError, "Invalid argument: not a PyBuffer");
    return NULL;
  }

  //Convert the object to a buffer object
  buffer = PyBuffer_FromObject(obj, 0, Py_END_OF_BUFFER);

  //This shouldn't be an error if the object passes the previous check
  if (buffer->ob_type->tp_as_buffer->bf_getreadbuffer == NULL){
    PyErr_SetString(PyExc_TypeError, "Invalid argument: not a readable PyBuffer");
    return NULL;
  }

  //Create an image_cap structure
  image_struct = malloc(sizeof(struct image_cap));

  //This call puts the size of PyBuffer object into image_struct.size
  //and sets the image_struct->data pointer to the beginning of the
  //PyBuffer's buffer
  image_struct->size = (int)(buffer->ob_type->tp_as_buffer->bf_getreadbuffer)\
                           (buffer, 0, &(image_struct->data));
  image_struct->handle = dev;
  
  if (Cfree_image(image_struct)){
    free(image_struct);
    PyErr_SetString(PyExc_IOError, "Error in C function call");
    return NULL;
  }
  
  return PyInt_FromLong(0L);
}

//Expects (int handle, int width, int height, int depth)
//Returns 0 upon success
static PyObject *refresh_image(PyObject *self, PyObject *args){
  int dev, w, h, d;
  struct image_cap image_struct;

  if(!PyArg_ParseTuple(args, "iiii", &dev, &w, &h, &d)){
    PyErr_SetString(PyExc_TypeError, "Invalid arguments to free_image");
    return NULL;
  }

  image_struct.handle = dev;
  image_struct.bpp = d;
  
  if(Crefresh_image(&image_struct, w, h)){
    PyErr_SetString(PyExc_IOError, "Error in C function call");
    return NULL;
  }

  return PyInt_FromLong(0L);
}

#include "../vision/vision.c"

static PyMethodDef grabImageMethods[] = {
  {"grab_image", grab_image, METH_VARARGS, "Grab an image from the camera"},
  {"refresh_image", refresh_image, METH_VARARGS, "Refresh the image"},
  {"free_image", free_image, METH_VARARGS, "Free memory from a grabbed image"},

#include "../vision/visionMethods.h"

  {NULL, NULL, 0, NULL}
};

void initgrabImage(void){
  (void) Py_InitModule("grabImage", grabImageMethods);
}
