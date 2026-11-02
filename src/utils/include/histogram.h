#ifndef __HISTOGRAM_H__
#define __HISTOGRAM_H__

#include <utils.h>

struct histogram {
  std::vector<int> array;
  double min;
  double max;
  double interval;
  
  void add(double value)
  {
    int pos;
    if (value >= max)
      {
        double i;
        for(i = max; i < value; i+= interval)
        {
          array.push_back(0);
        }
        max = i;
        array.push_back(1);
      }
    else if(value < min)
    {
      double i;
      for(i  = min; i > value; i -= interval)
      {
        array.insert(array.cbegin(), 0);
      }
      min = i;
      array.insert(array.cbegin(), 1);
    }
    else
    {
      pos = (min < 0) ? (value - min) / interval : value / interval;
      array.at(pos) += 1;
    }
  }
};

#endif // __HISTOGRAM_H__
