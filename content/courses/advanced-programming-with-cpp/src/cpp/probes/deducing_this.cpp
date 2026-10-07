// P0847 explicit object parameter ("deducing this")
struct S { int v = 0; auto&& get(this auto&& self) { return self.v; } };
int main() { S s; return s.get(); }
