#include "RWLock.h"

RWLock::RWLock(void)
{
	pthread_mutex_init(&m_CountLock,NULL);
	pthread_mutex_init(&m_AccessLock,NULL);
	m_lCount = 0;
}

RWLock::~RWLock(void)
{
	pthread_mutex_destroy(&m_CountLock);
	pthread_mutex_destroy(&m_AccessLock);
}

void RWLock::ReadLock(void)
{
	pthread_mutex_lock(&m_CountLock);
	m_lCount++;
	if (m_lCount == 1)
		pthread_mutex_lock(&m_AccessLock);
	pthread_mutex_unlock(&m_CountLock);
}

void RWLock::ReadUnlock(void)
{
	pthread_mutex_lock(&m_CountLock);
	m_lCount--;
	if (m_lCount == 0)
		pthread_mutex_unlock(&m_AccessLock);
	pthread_mutex_unlock(&m_CountLock);
}

void RWLock::WriteLock(void)
{
	pthread_mutex_lock(&m_AccessLock);
}

void RWLock::WriteUnlock(void)
{
	pthread_mutex_unlock(&m_AccessLock);
}
