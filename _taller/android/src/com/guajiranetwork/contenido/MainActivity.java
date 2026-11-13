package com.guajiranetwork.contenido;

import android.Manifest;
import android.app.Activity;
import android.app.DownloadManager;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.view.View;
import android.view.Window;
import android.webkit.DownloadListener;
import android.webkit.JavascriptInterface;
import android.webkit.URLUtil;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/** Guajira Network · Centro de Contenido.
 *  Abre la app web y le da un puente nativo (window.GNAndroid) para:
 *  compartir el ARCHIVO ORIGINAL directo a WhatsApp, guardarlo en la galería y copiar el texto. */
public class MainActivity extends Activity {

    static final String URL_APP = "https://nodo-link.github.io/guajiranetwork.contenido/";
    static final String HOST = "nodo-link.github.io";
    WebView web;

    @Override
    protected void onCreate(Bundle estado) {
        super.onCreate(estado);
        Window w = getWindow();
        w.setStatusBarColor(Color.WHITE);
        w.setNavigationBarColor(Color.WHITE);
        int flags = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
        if (Build.VERSION.SDK_INT >= 26) flags |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        w.getDecorView().setSystemUiVisibility(flags);

        web = new WebView(this);
        web.setBackgroundColor(Color.WHITE);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setUserAgentString(s.getUserAgentString() + " GuajiraNetworkApp/1");

        web.addJavascriptInterface(new Puente(), "GNAndroid");
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                if (HOST.equals(u.getHost())) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) { }
                return true;
            }
            @Override
            public void onReceivedError(WebView v, WebResourceRequest r, WebResourceError e) {
                if (r.isForMainFrame()) sinConexion();
            }
        });
        web.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String ua, String cd, String mime, long largo) {
                if (url.startsWith("http")) descargar(null, url, URLUtil.guessFileName(url, cd, mime), mime);
            }
        });

        if (estado != null) web.restoreState(estado);
        else web.loadUrl(URL_APP);
    }

    @Override protected void onSaveInstanceState(Bundle b) { super.onSaveInstanceState(b); web.saveState(b); }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }

    void sinConexion() {
        String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>"
            + "<style>body{margin:0;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:sans-serif;color:#1C1B29;text-align:center;padding:24px;box-sizing:border-box}"
            + "h1{font-size:20px;margin:22px 0 6px}p{color:#6B6880;font-size:14px;margin:0 0 22px}"
            + "button{border:0;border-radius:14px;height:50px;padding:0 28px;font-size:15px;font-weight:600;color:#fff;background:linear-gradient(135deg,#4F46E5,#6D28D9)}</style></head><body>"
            + "<svg width='72' height='72' viewBox='0 0 64 64'><rect width='64' height='64' rx='16' fill='#4F46E5'/><path d='M17 19l13 13-13 13' fill='none' stroke='#C4B5FD' stroke-width='7.5' stroke-linecap='round' stroke-linejoin='round'/><path d='M33 19l13 13-13 13' fill='none' stroke='#fff' stroke-width='7.5' stroke-linecap='round' stroke-linejoin='round'/></svg>"
            + "<h1>Sin conexión</h1><p>Revisa tu internet e inténtalo de nuevo.</p><button onclick='GNAndroid.reintentar()'>Reintentar</button></body></html>";
        web.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    /** Devuelve el resultado a la página: window.__gn[id]({ok, msg}) */
    void responder(final String id, boolean ok, String msg) {
        if (id == null || !id.matches("[A-Za-z0-9_]+")) return;
        try {
            JSONObject o = new JSONObject();
            o.put("ok", ok);
            o.put("msg", msg == null ? "" : msg);
            final String js = "window.__gn&&window.__gn['" + id + "']&&window.__gn['" + id + "'](" + o + ")";
            runOnUiThread(new Runnable() { public void run() { web.evaluateJavascript(js, null); } });
        } catch (Exception ignored) { }
    }

    /** Descarga el archivo original a la caché para compartirlo. */
    File bajar(String url, String nombre) throws Exception {
        File dir = new File(getCacheDir(), "compartir");
        if (!dir.exists()) dir.mkdirs();
        File[] viejos = dir.listFiles();
        if (viejos != null) for (File f : viejos) f.delete();
        File destino = new File(dir, new File(nombre).getName());
        String actual = url;
        for (int i = 0; i < 5; i++) {
            HttpURLConnection c = (HttpURLConnection) new URL(actual).openConnection();
            c.setInstanceFollowRedirects(false);
            c.setUseCaches(false);
            c.setConnectTimeout(20000);
            c.setReadTimeout(60000);
            int code = c.getResponseCode();
            if (code >= 300 && code < 400) { actual = new URL(new URL(actual), c.getHeaderField("Location")).toString(); c.disconnect(); continue; }
            if (code != 200) throw new Exception("HTTP " + code);
            InputStream in = c.getInputStream();
            OutputStream out = new FileOutputStream(destino);
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            out.close(); in.close(); c.disconnect();
            return destino;
        }
        throw new Exception("Demasiadas redirecciones");
    }

    void descargar(String id, String url, String nombre, String mime) {
        try {
            if (Build.VERSION.SDK_INT < 29 && checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, 7);
                responder(id, false, "permiso");
                return;
            }
            boolean video = mime != null && mime.startsWith("video");
            String carpeta = video ? Environment.DIRECTORY_MOVIES : Environment.DIRECTORY_PICTURES;
            DownloadManager.Request r = new DownloadManager.Request(Uri.parse(url));
            r.setTitle(nombre);
            r.setDescription("Guajira Network");
            if (mime != null && !mime.isEmpty()) r.setMimeType(mime);
            r.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            r.setDestinationInExternalPublicDir(carpeta, "Guajira Network/" + nombre);
            ((DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE)).enqueue(r);
            responder(id, true, video ? "Películas › Guajira Network" : "Imágenes › Guajira Network");
        } catch (Exception e) {
            responder(id, false, e.toString());
        }
    }

    class Puente {
        @JavascriptInterface public String version() { return "1"; }

        @JavascriptInterface public void copiar(String texto) {
            ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
            cm.setPrimaryClip(ClipData.newPlainText("Guajira Network", texto));
        }

        @JavascriptInterface public void reintentar() {
            runOnUiThread(new Runnable() { public void run() { web.loadUrl(URL_APP); } });
        }

        @JavascriptInterface public void descargar(String id, String url, String nombre, String mime) {
            MainActivity.this.descargar(id, url, nombre, mime);
        }

        @JavascriptInterface public void compartir(final String id, final String url, final String nombre, final String mime, final String texto) {
            new Thread(new Runnable() {
                public void run() {
                    try {
                        File f = bajar(url, nombre);
                        Uri u = Uri.parse("content://" + Archivos.AUTORIDAD + "/" + Uri.encode(f.getName()));
                        Intent i = new Intent(Intent.ACTION_SEND);
                        i.setType(mime);
                        i.putExtra(Intent.EXTRA_STREAM, u);
                        if (texto != null && !texto.isEmpty()) i.putExtra(Intent.EXTRA_TEXT, texto);
                        i.setClipData(ClipData.newRawUri(f.getName(), u));
                        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        final Intent elegir = Intent.createChooser(i, "Publicar en…");
                        elegir.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        runOnUiThread(new Runnable() { public void run() { startActivity(elegir); } });
                        responder(id, true, "");
                    } catch (Exception e) {
                        responder(id, false, e.toString());
                    }
                }
            }).start();
        }
    }
}
