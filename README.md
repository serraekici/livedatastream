# livedatastream



 UYGULAMANIN GENEL BİLGİSİ
Bu uygulama, STM32 mikrodenetleyicisinden alınan verileri UART seri haberleşme aracılığıyla gerçek zamanlı olarak işleyip grafiğe dönüştüren bir canlı veri izleme sistemidir. Tasarımı, özellikle biyolojik sinyaller, beyin sinyalleri gibi hassas ve gürültülü sinyallerin izlenmesi ve analiz edilmesi için optimize edilmiştir. Gerçeğe yakın olabilmesi için veri formatları, kalp atışı formatında izleniyor. Sistem, kullanıcının verileri gerçek zamanlı olarak görüntüleyip analiz etmesine olanak tanıyan çeşitli işlevselliklere sahiptir.
Uygulamanın ana işlevi, mikrodenetleyiciden alınan verilerin gerçek zamanlı olarak grafikte gösterilmesidir. Kullanıcı, 10 farklı kanal arasından istediği sayıda kanalı seçerek bu kanalları eş zamanlı olarak izleyebilir. İhtiyaç halinde kanal sayısı 40'a kadar çıkarılacak şekilde tasarlanabilir.
Kullanıcının dilediği kanalların ortalamasını grafikte göstermek de mümkündür; bu özellik, özellikle beyin sinyallerinin analizi sırasında kullanıcılara büyük bir kolaylık sağlar.
Uygulama, veri kaynağı seçimi konusunda da esneklik sunar. Kullanıcı, uygulamayı başlattığında 'Import From File' (Dosyadan Aktarım) veya 'USB Serial Device' seçeneklerinden birini tercih edebilir. Dosya aktarma seçeneği, bilgisayardaki dosyaların belirtilen formatlarda grafiğe aktarılmasını sağlar.
Mikrodenetleyiciden alınan gerçek zamanlı veriler, otomatik olarak bir CSV dosyasına kaydedilir ve ardından bu dosya üzerinden veri aktarım ekranı aracılığıyla grafikte görüntülenir. Bu özellik, verilerin kaybolmasını önleyerek kullanıcıların bu dosyaları izleyebilmesine olanak tanır. Dosyadan veri aktarımı ekranı, seri cihaz ekranıyla benzer bir arayüz sunarak kullanıcıya tanıdık bir deneyim sağlar.
Uygulamanın grafik arayüzü, kullanıcının x-y limit değerlerini manuel olarak ayarlamasına imkan verir. Bu sayede, grafik üzerinde belirli bir bölgeye yakınlaşmak ya da uzaklaşmak mümkün olur, böylece verilerin detaylı incelemesi yapılabilir.
Grafiklerin sol tarafında bulunan terminal alanı, mikrodenetleyiciden gelen ham verileri anlık olarak gösterir. Bu alan, verilerin doğrudan izlenmesi ve gürültülü sinyallerin analiz edilmesi açısından önemlidir. 
Kullanıcı, terminaldeki verileri temizlemek için "Clear" butonunu kullanabilir; bu buton, hem terminal ekranını hem de grafikleri sıfırlayarak yeni veri akışına yer açar.
Ayrıca, uygulama Kalman filtresi entegrasyonuna sahiptir. Kalman filtresi, özellikle gürültülü verilerin analizinde sinyalin gerçek değerine daha yakın sonuçlar elde edilmesine olanak tanır. Bu filtre, kullanıcı tarafından aktif hale getirildiğinde, beyin sinyalleri gibi hassas verilerin daha net bir şekilde analiz edilmesini sağlar.
