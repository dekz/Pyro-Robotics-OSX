/*
  This is a class to implement a lock for multiple writers and single readers,
  it will allow as many reader locks to go unblocked so long as one reader
  has a block, and will let only one reader block at a time
*/
#ifndef __RWLOCK_H__
#define __RWLOCK_H__

#include <pthread.h>

class RWLock {
private:
	long m_lCount;
	pthread_mutex_t m_CountLock,m_AccessLock;
public:
	RWLock(void);
	~RWLock(void);
	
	void ReadLock(void);
	void ReadUnlock(void);
	void WriteLock(void);
	void WriteUnlock(void);
};

#endif
