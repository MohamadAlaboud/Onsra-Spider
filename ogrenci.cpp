class Student {
public:
    string name;
    int age;

    // 1. Kurucu: Hic parametre almazsa (Default)
    Student() {
        name = "Bilinmiyor";
        age = 0;
        cout << "Varsayilan kurucu calisti." << endl;
    }

    // 2. Kurucu: Isim ve yas verilirse (Parameterized) [cite: 52, 112]
    Student(string n, int a) {
        name = n;
        age = a;
        cout << name << " sisteme kaydedildi." << endl;
    }

    ~Student() {
        cout << name << " objesi yok ediliyor." << endl;
    }
};