import vision

class VisionSystem(vision.Vision):
    """
    Things a vision system must provide:

    1. vision.registerCameraDevice(self.cameraDevice)
    2. vision.getWidth()
    3. vision.getHeight()
    4. vision.getDepth()
    5. vision.getMMap()

    Things that would be handy, to integrate with filters:
    1. vision.setFilterList(myList)
    2. vision.applyFilterList()
    3. vision.popFilterList()
    4. vision.getFilterList()
    5. vision.applyFilters(filters)
    6. vision.addFilter()
    7. vision.get(x, y)

    Other functions, here or there:
    1. getCopyMode()
    
    """

    def __init__(self):
        vision.Vision.__init__(self)

