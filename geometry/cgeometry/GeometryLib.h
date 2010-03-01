#ifndef __GEOMETRY_H__
#define __GEOMETRY_H__

#include <Python.h>
#include <stdlib.h>
#include <math.h>

class World {
 public:
  World();
};

class Point {
 public:
  double x, y;
  Point(double x, double y);
  Point();
};

class Segment {
 public:
  double x1, y1, x2, y2;
  PyObject *start, *end;
  int id;
  Segment(double x1, double y1, double x2, double y2, int id = 0);
  Segment(PyObject *start, PyObject *end, int id = 0);
  ~Segment();
  double angle();
  double length();
  bool in_bbox(double x, double y);
  bool parallel(Segment *other);
  bool vertical();
  double slope();
  Point *intersection(Segment *other);
  PyObject *intersects(Segment *other);
  double yintercept();
};

#endif 
