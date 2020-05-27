def repr_short(self):
    return self.name + str(self.label[0]) + (".D" if self.d else "")
