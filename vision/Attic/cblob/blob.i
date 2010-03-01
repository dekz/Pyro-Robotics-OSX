%module blob

%typemap(in) cbuf_t {
	int i;
	char* ptr;
	PyObject_AsReadBuffer($input, &ptr, &i);
	$1 = (uint8_t*) ptr;
}
%include "blob.h"
struct blob* blob_at(struct blob** list, int i) {return list[i];}
%{
#include "blob.h"

typedef double (*FILTER_FUNC)(double, double, double);
const FILTER_FUNC FILTER_RED = filter_red;
const FILTER_FUNC FILTER_BLUE = filter_blue;
const FILTER_FUNC FILTER_GREEN = filter_green;
const FILTER_FUNC FILTER_HUE = filter_hue;
const FILTER_FUNC FILTER_SATURATION = filter_saturation;
const FILTER_FUNC FILTER_BRIGHTNESS = filter_brightness;
struct blob* blob_at(struct blob** list, int i) {return list[i];}
%}
typedef double (*FILTER_FUNC)(double, double, double);
const FILTER_FUNC FILTER_RED = filter_red;
const FILTER_FUNC FILTER_BLUE = filter_blue;
const FILTER_FUNC FILTER_GREEN = filter_green;
const FILTER_FUNC FILTER_HUE = filter_hue;
const FILTER_FUNC FILTER_SATURATION = filter_saturation;
const FILTER_FUNC FILTER_BRIGHTNESS = filter_brightness;

