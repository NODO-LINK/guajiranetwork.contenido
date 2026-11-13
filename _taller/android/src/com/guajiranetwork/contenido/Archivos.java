package com.guajiranetwork.contenido;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;

/** Entrega a WhatsApp (solo lectura) el archivo original descargado en la caché. */
public class Archivos extends ContentProvider {

    static final String AUTORIDAD = "com.guajiranetwork.contenido.archivos";

    File archivo(Uri u) {
        String n = u.getLastPathSegment();
        return new File(new File(getContext().getCacheDir(), "compartir"), new File(n == null ? "" : n).getName());
    }

    @Override public boolean onCreate() { return true; }

    @Override
    public ParcelFileDescriptor openFile(Uri u, String modo) throws FileNotFoundException {
        File f = archivo(u);
        if (!f.exists()) throw new FileNotFoundException(f.getName());
        return ParcelFileDescriptor.open(f, ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override
    public String getType(Uri u) {
        String n = archivo(u).getName().toLowerCase();
        if (n.endsWith(".mp4")) return "video/mp4";
        if (n.endsWith(".mov")) return "video/quicktime";
        if (n.endsWith(".png")) return "image/png";
        if (n.endsWith(".webp")) return "image/webp";
        return "image/jpeg";
    }

    @Override
    public Cursor query(Uri u, String[] p, String s, String[] a, String o) {
        File f = archivo(u);
        MatrixCursor c = new MatrixCursor(new String[]{OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE});
        c.addRow(new Object[]{f.getName(), f.length()});
        return c;
    }

    @Override public Uri insert(Uri u, ContentValues v) { return null; }
    @Override public int delete(Uri u, String s, String[] a) { return 0; }
    @Override public int update(Uri u, ContentValues v, String s, String[] a) { return 0; }
}
