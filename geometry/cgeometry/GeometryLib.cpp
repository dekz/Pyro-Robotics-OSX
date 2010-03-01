#include "GeometryLib.h"

World::World() {
}

Point::Point() {
  x = 0.0;
  y = 0.0;
}

Point::Point(double x, double y) {
  this->x = x;
  this->y = y;
}

Segment::Segment(PyObject *start, PyObject *end, int id) {
  if (!PyArg_ParseTuple(start, "dd", &x1, &y1)) {
    PyErr_SetString(PyExc_AttributeError, "invalid argument to Segment");
  }
  if (!PyArg_ParseTuple(end, "dd", &x2, &y2)) {
    PyErr_SetString(PyExc_AttributeError, "invalid argument to Segment");
  }
  this->start = Py_BuildValue("(dd)", x1, y1);
  this->end = Py_BuildValue("(dd)", x2, y2);
  this->id = id;
}

Segment::Segment(double x1, double y1, double x2, double y2, int id) {
  this->x1 = x1;
  this->y1 = y1;
  this->x2 = x2;
  this->y2 = y2;
  this->id = id;
  this->start = Py_BuildValue("(dd)", x1, y1);
  this->end = Py_BuildValue("(dd)", x2, y2);
}

Segment::~Segment() {
  Py_DECREF(start);
  Py_DECREF(end);
}

double Segment::angle() {
  return atan2(y2 - y1, x2 - x1);
}

double Segment::length() {
  return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2));
}

bool Segment::in_bbox(double x, double y){
  return ((((x <= x1) && (x >= x2)) || ((x <= x2) && (x >= x1))) &&
	  (((y <= y1) && (y >= y2)) || ((y <= y2) && (y >= y1))));
}

bool Segment::parallel(Segment *other) {
  if (vertical())
    return other->vertical();
  else if (other->vertical())
    return false;
  else
    return (slope() == other->slope());
}

bool Segment::vertical() {
  return (x1 == x2);
}

double Segment::slope() {
  return (y2 - y1)/(x2 - x1);
}

Point *Segment::intersection(Segment *other) {
  if (parallel(other))
    // the segments may intersect, but we don't care
    return NULL;
  else if (vertical()) 
    return other->intersection(this);
  else if (other->vertical())
    return new Point(other->x1, yintercept() + other->x1 * slope());
  else {
    // m1x + b1 = m2x + b2; so
    // (m1 - m2)x + b1 - b2 == 0
    // (m1 - m2)x = b2 - b1
    // x = (b2 - b1)/(m1 - m2)
    double x = ((other->yintercept() - yintercept()) / (slope() - other->slope()));
    return new Point(x, yintercept() + x * slope());
  }
}

PyObject *Segment::intersects(Segment *other) {
  PyObject *retval = NULL;
  Point *p = NULL;
  if (parallel(other)) {
    // they can "intersect" if they are collinear and overlap
    if (!(in_bbox(other->x1, other->y1) || in_bbox(other->x2, other->y2))) {
      retval = Py_BuildValue("");
    } else if (vertical()) {
      if (x1 == other->x1) {
	p = intersection(other);
	if (p != NULL)
	  retval = Py_BuildValue("(dd)", p->x, p->y);
	else
	  retval = Py_BuildValue("");
      } else 
	retval = Py_BuildValue("");
    } else {
      if (yintercept() == other->yintercept()) {
	p = intersection(other);
	if (p != NULL)
	  retval = Py_BuildValue("(dd)", p->x, p->y);
	else
	  retval = Py_BuildValue("i", 0);
      } else {
	retval = Py_BuildValue("");
      }
    }
  } else {
    p = intersection(other);
    if (p != NULL) {
      if (in_bbox(p->x, p->y) && other->in_bbox(p->x, p->y)) {
	retval = Py_BuildValue("(dd)", p->x, p->y);
      } else {
	retval = Py_BuildValue("");
      }
    } else
      retval = Py_BuildValue("");
  }
  delete p;
  return retval;
}

double Segment::yintercept() {
  return (y1 - x1 * slope());
}
