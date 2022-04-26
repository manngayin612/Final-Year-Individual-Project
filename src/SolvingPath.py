class SolvingPath(object):
    def __init__(self, condition, cond_arg=None, next_steps=None, is_leaf=False):
        
        self.condition = condition
        self.cond_arg = cond_arg
        self.children =  []
        self.is_leaf = is_leaf

        if next_steps is not None:
            for next in next_steps:
                
                self.children.append(next)
        if is_leaf:
            assert len(self.children)==0


    # def __repr__(self):
    #     return self.condition

    def add_new_paths(self, node):
        assert isinstance(node, SolvingPath)
        self.children.append(node)

    def checkCondition(self):
        return self.condition(self.cond_arg)


