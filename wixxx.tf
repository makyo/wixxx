/loaded wixxx.tf
;;;;;
; wixxx logging
;
; Sets up commands and triggers for logging wixxx flags.
;
; Note that you'll need some variables set for this. You should have another
; wixxx-info.tf file that you load in .tfrc looking something like:
; 
; /set WIXXX_USER=wixxx_username
; /set WIXXX_SECRET=wwixxx_secret
; /export WIXXX_USER
; /export WIXXX_SECRET
; /set wixxx_python=/path/to/wixxx/venv/bin/python
; /set wixxx_client=/path/to/wixxx/wixxx-client.py
; /set wixxx_server=https://wixxx.vis.adjectivespecies.com

;;; The following need to be wrapped in two layers of closures for reasons I
;;; don't totally understand. Doing them in one layer (that is, getting rid of
;;; do_wixxx_write and just having the closure in create_wixxx_write write the
;;; line) produces `% create_wixxx_write: unexpected /ENDIF in outer block`.

/def create_wixxx_write = /def -F -p2 -ag -mregexp -t"^(.+)$$" wixxx_write = \
	$do_wixxx_write

;; Log a normal wixxx line to a file.
/def do_wixxx_write = \
	/if (wixxx_fh != -1) \
		/test tfwrite(wixxx_fh, {P1})%; \
	/endif

/def create_wixxx_stop = /def -F -p3 -ag -mregexp -t"^(-------------------------------------------------------- by K'T/AnnonyMouse --)$$" wixxx_stop = \
	$do_wixxx_stop

;; Stop logging wixxx.
;
; Take the following actions:
; - Write the final wixxx line to the file
; - Close the file
; - Delete these macross
; - Call the client.
/def do_wixxx_stop = \
	/if (wixxx_fh != -1) \
		/test tfwrite(wixxx_fh, {P1})%; \
		/test tfclose(wixxx_fh)%; \
	/endif%; \
	/set wixxx_fh=-1 %; \
	/undef wixxx_write%; \
	/undef wixxx_stop%; \
;; Write the line silently. Comment this out and uncomment the line after to
;; receive a notification
	/eval /quote /set wixxx_output !echo `%%{wixxx_python} %%{wixxx_client} --server %%{wixxx_server} %%{logname}` `date`&& rm %%{logname}
;/eval /quote /echo :::wixxx-client: !%%{wixxx_python} %%{wixxx_client} --server %%{wixxx_server} %%{logname} && rm %%{logname}

;; Start the process of logging wixxx.
;
; Take the following action:
; - Open the file with a unique filename
; - Create the macros
; - Send the wixxx command
/def logwixxx = \
	/eval /set logname /tmp/wixxx.${world_name}.$[ftime("%@")]%; \
	/set wixxx_fh=$[tfopen(logname, "w")]%; \
	/if (wixxx_fh != -1) \
		/create_wixxx_write%; \
		/create_wixxx_stop%; \
;/eval /echo :::wixxx: %{*}%; \
		/send wixxx %{*}%; \
	/endif

;; Trigger to log wixxx.
;
; Use a regexp to capture any names in case you only want to wixxx those.
; The match should come quoted - e.g:
; /wixxx_trigger `foo`
/def wixxx_trigger = \
	/def -F -p2 -mregexp -t%{*} = /logwixxx %%{P1}
